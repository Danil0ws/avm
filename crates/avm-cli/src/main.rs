use anyhow::Result;
use clap::{Parser, Subcommand};

mod commands;

#[derive(Parser)]
#[command(
    name = "avm",
    version = env!("CARGO_PKG_VERSION"),
    about = "AVM - All Version Manager",
    long_about = "AVM manages versions of development tools without relying on other version managers."
)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Show system information
    System,
    /// List available providers
    Providers,
    /// Run diagnostics
    Doctor,
    /// Catalog commands
    Catalog {
        #[command(subcommand)]
        cmd: CatalogCommands,
    },
    /// List available versions for a tool
    Available {
        tool: String,
        #[arg(long)]
        all: bool,
        #[arg(long)]
        lts: bool,
        #[arg(long)]
        distribution: Option<String>,
        #[arg(long)]
        os: Option<String>,
        #[arg(long)]
        arch: Option<String>,
    },
    /// Show detailed info about a version
    Info {
        spec: String,
    },
    /// Install a tool version
    Install {
        spec: String,
        #[arg(long)]
        os: Option<String>,
        #[arg(long)]
        arch: Option<String>,
    },
    /// List installed versions
    Installed,
    /// Show current active versions
    Current {
        tool: Option<String>,
    },
    /// Show install path for a version
    Path {
        spec: String,
    },
    /// Uninstall a version
    Uninstall {
        spec: String,
    },
    /// Execute a command with a tool version
    Exec {
        #[arg(trailing_var_arg = true)]
        args: Vec<String>,
    },
}

#[derive(Subcommand)]
enum CatalogCommands {
    /// Show catalog status
    Status,
    /// Refresh catalog from remote
    Refresh,
}

fn main() -> Result<()> {
    tracing_subscriber::fmt()
        .with_env_filter(
            tracing_subscriber::EnvFilter::from_default_env()
                .add_directive("avm=info".parse().unwrap()),
        )
        .init();

    let cli = Cli::parse();

    match cli.command {
        Commands::System => commands::system::run(),
        Commands::Providers => commands::providers::run(),
        Commands::Doctor => commands::doctor::run(),
        Commands::Catalog { cmd } => match cmd {
            CatalogCommands::Status => commands::catalog::status(),
            CatalogCommands::Refresh => commands::catalog::refresh(),
        },
        Commands::Available { tool, all, lts, distribution, os, arch } => {
            commands::available::run(&tool, all, lts, distribution.as_deref(), os.as_deref(), arch.as_deref())
        }
        Commands::Info { spec } => commands::info::run(&spec),
        Commands::Install { spec, os, arch } => {
            commands::install::run(&spec, os.as_deref(), arch.as_deref())
        }
        Commands::Installed => commands::installed::run(),
        Commands::Current { tool } => commands::current::run(tool.as_deref()),
        Commands::Path { spec } => commands::path::run(&spec),
        Commands::Uninstall { spec } => commands::uninstall::run(&spec),
        Commands::Exec { args } => commands::exec::run(&args),
    }
}

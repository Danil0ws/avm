

# PROMPT COMPLEMENTAR — AVM: EXPANSÃO PARA OUTRAS LINGUAGENS

## 1. Contexto

Você está trabalhando no AVM (All Version Manager), um gerenciador universal de versões implementado em Rust.

Já existe um plano inicial para suportar:

- Java: distribuição Eclipse Temurin.

- Node.js: distribuições oficiais do Node.js.

Agora, amplie a arquitetura para suportar outras linguagens, runtimes, SDKs e ferramentas de desenvolvimento.

**Objetivo:** transformar o AVM em um gerenciador extensível de versões, sem depender de outros version managers como backend.

Antes de implementar, inspecione o repositório existente. Preserve a arquitetura, os comandos, os formatos de catálogo e os contratos que já funcionam. Não reescreva funcionalidades existentes sem necessidade.

## 2. Linguagens e ferramentas prioritárias

Implemente os providers na ordem abaixo, respeitando a arquitetura já existente.

### Fase 1 — Linguagens prioritárias

| Provider | Linguagem/runtime | Fonte oficial preferencial |

|---|---|---|

| Python | Python | [python.org](http://python.org) e metadados oficiais de releases |

| Go | Go | [go.dev/dl](http://go.dev/dl) |

| .NET | SDK .NET | [builds.dotnet.microsoft.com](http://builds.dotnet.microsoft.com) e feeds oficiais da Microsoft |

| PHP | PHP | [php.net](http://php.net) e distribuidores oficiais por plataforma |

| Ruby | Ruby | [ruby-lang.org](http://ruby-lang.org) e arquivos oficiais de distribuição |

| Rust | Rust toolchain | canais oficiais de distribuição de Rust |

### Fase 2 — Ecossistema JavaScript e JVM

| Provider | Ferramenta | Fonte preferencial |

|---|---|---|

| Bun | Runtime JavaScript | [bun.sh](http://bun.sh) e releases oficiais |

| Deno | Runtime JavaScript/TypeScript | [deno.com](http://deno.com) e releases oficiais |

| Kotlin | Compilador/SDK | Kotlin e JetBrains |

| Scala | Compilador/SDK | [scala-lang.org](http://scala-lang.org) e repositórios oficiais |

| Maven | Build tool Java | [maven.apache.org](http://maven.apache.org) |

| Gradle | Build tool JVM | [gradle.org](http://gradle.org) |

### Fase 3 — Ecossistema de desenvolvimento

| Provider | Ferramenta | Fonte preferencial |

|---|---|---|

| Elixir | Linguagem/runtime | [elixir-lang.org](http://elixir-lang.org) |

| Erlang/OTP | Runtime Erlang | [erlang.org](http://erlang.org) |

| Dart | SDK Dart | [dart.dev](http://dart.dev) |

| Flutter | SDK Flutter | [flutter.dev](http://flutter.dev) |

| Zig | Compilador Zig | [ziglang.org](http://ziglang.org) |

| CMake | Build tool | [cmake.org](http://cmake.org) |

| Terraform | Infraestrutura como código | [releases.hashicorp.com](http://releases.hashicorp.com) |

| OpenTofu | Infraestrutura como código | [opentofu.org](http://opentofu.org) |

| kubectl | Cliente Kubernetes | [kubernetes.io](http://kubernetes.io) |

A lista é um roadmap, não uma obrigação de implementar todos imediatamente.

Não declare um provider funcional apenas porque existe uma definição de configuração. Cada provider deve ter resolução de versões, seleção de artefatos, instalação, verificação e testes compatíveis com o seu contrato.

## 3. Regras obrigatórias

1. Não utilizar mise, asdf, vfox, nvm, fnm, Volta, pyenv, rustup, SDKMAN ou outros gerenciadores de versões como backend.

2. Implementar o gerenciamento de versões dentro do AVM.

3. Permitir baixar os artefatos oficiais diretamente dos respectivos distribuidores.

4. Não compilar runtimes a partir do código-fonte automaticamente como caminho padrão.

5. Não exigir privilégios de administrador para a instalação padrão.

6. Não modificar PATH global, registry do sistema ou arquivos de configuração do usuário silenciosamente.

7. Não executar scripts remotos de instalação.

8. Não inventar URLs, hashes, assinaturas ou metadados.

9. Não assumir que todos os providers suportam todas as plataformas.

10. Não quebrar a compatibilidade dos providers Java e Node.js já existentes.

Bibliotecas Rust genéricas para HTTP, serialização, arquivos compactados, hashing, assinaturas e gerenciamento de processos são permitidas.

## 4. Arquitetura extensível

Crie ou adapte uma abstração comum de provider, respeitando os padrões existentes no projeto.

A abstração deve contemplar, conceitualmente:

- Identificação do provider.

- Nome e descrição da ferramenta.

- Consulta de versões disponíveis.

- Resolução de aliases, canais e versões exatas.

- Seleção de versão por sistema operacional e arquitetura.

- Seleção de distribuição ou variante.

- Resolução de URL e metadados do artefato.

- Verificação de integridade e autenticidade.

- Download e instalação.

- Identificação do executável principal.

- Verificação da instalação.

- Remoção segura de versões instaladas.

- Geração das variáveis de ambiente necessárias para executar a ferramenta.

Exemplo conceitual:

\`\`\`rust

trait VersionProvider {

    fn id(&amp;self) -&gt; &amp;'static str;

    async fn available\_versions(

        &amp;self,

        request: &amp;VersionRequest,

    ) -&gt; Result&lt;Vec&lt;VersionInfo&gt;&gt;;

    async fn resolve(

        &amp;self,

        request: &amp;VersionRequest,

        platform: &amp;Platform,

    ) -&gt; Result&lt;ResolvedArtifact&gt;;

    async fn install(

        &amp;self,

        artifact: &amp;ResolvedArtifact,

        destination: &amp;Path,

    ) -&gt; Result&lt;InstalledTool&gt;;

    fn executables(

        &amp;self,

        installation: &amp;InstalledTool,

    ) -&gt; Result&lt;Vec&lt;ExecutableInfo&gt;&gt;;

}

\`\`\`

O código acima é apenas uma referência de design. Adapte assinaturas, tipos e async runtime ao código existente. Não copie interfaces incompatíveis com a arquitetura real.

Evite criar um único arquivo gigante com condicionais para todas as linguagens.

Organize os providers em módulos independentes e reutilize o núcleo de download, verificação, extração, armazenamento e execução.

## 5. Modelo de metadados

Defina um modelo comum para versões e artefatos.

Cada versão poderá conter:

- Nome do provider.

- Versão original e versão normalizada.

- Canal: stable, preview, beta, nightly, LTS ou equivalente.

- Distribuição, quando aplicável.

- Data de lançamento, se disponível.

- Estado de suporte, se publicado oficialmente.

- Plataformas e arquiteturas compatíveis.

- URLs dos artefatos oficiais.

- SHA-256 ou outro checksum oficialmente publicado.

- Dados de assinatura, quando disponíveis.

- Tipo de pacote e método de extração.

- Executáveis e diretórios importantes.

- Variáveis de ambiente necessárias.

- Fonte dos metadados e data da última atualização.

Não force linguagens diferentes a compartilhar semânticas artificiais.

Por exemplo:

- Python possui diferentes tipos de distribuição e disponibilidade de builds por plataforma.

- Go possui arquivos compactados oficiais para diferentes sistemas e arquiteturas.

- .NET diferencia SDKs, runtimes e workloads.

- Rust possui toolchains, canais e componentes.

- PHP tem disponibilidade e métodos de distribuição diferentes entre Windows, macOS e Linux.

- Flutter pode precisar de Git, componentes adicionais e downloads separados.

Modele as diferenças usando tipos específicos ou capacidades opcionais, sem enfraquecer o contrato comum.

## 6. Catálogo automatizado

Expanda o catálogo para incorporar novos providers sem transformar o workflow em uma sequência de scripts frágeis.

Estrutura sugerida:

\`\`\`text

catalog/

├── collectors/

│   ├── java/

│   ├── node/

│   ├── python/

│   ├── go/

│   ├── dotnet/

│   ├── php/

│   ├── ruby/

│   └── rust/

├── schemas/

├── tests/

└── public/

    ├── index.json

    ├── catalog.json

    ├── tools/

    │   ├── java.json

    │   ├── node.json

    │   ├── python.json

    │   ├── go.json

    │   ├── dotnet.json

    │   ├── php.json

    │   ├── ruby.json

    │   └── rust.json

    └── schema/

\`\`\`

Adapte a estrutura caso o catálogo já tenha outro layout funcional.

### Requisitos do coletor

- Consultar somente fontes oficiais ou fontes cuja procedência e confiabilidade estejam documentadas.

- Normalizar versões sem descartar a versão original.

- Validar os dados contra schemas.

- Deduplicar releases.

- Tratar rate limits, falhas de rede e respostas inválidas.

- Gerar resultados determinísticos.

- Não publicar dados incompletos como se fossem válidos.

- Preservar o último catálogo válido se uma fonte falhar.

- Registrar erros por provider, sem interromper desnecessariamente todos os demais.

- Atualizar os metadados em workflow agendado e sob demanda.

- Usar permissões mínimas no GitHub Actions.

- Fixar Actions em SHAs de commit em ambientes de produção.

- Não colocar tokens ou credenciais no catálogo.

A atualização de um provider deve ser independente. Uma falha na fonte de PHP, por exemplo, não deve apagar os dados válidos de Python, Java ou Node.js.

## 7. Instalação multiplataforma

Suportar inicialmente:

- Windows 10/11 x64.

- Windows ARM64, quando houver artefatos oficiais compatíveis.

- macOS x64.

- macOS ARM64.

- Linux x64.

- Linux ARM64.

Para cada provider, documente a matriz real de suporte.

O AVM deve selecionar automaticamente o artefato compatível com o sistema e a arquitetura detectados, respeitando as restrições do provider.

Considere:

- Arquivos ZIP e TAR.

- Arquivos compactados com formatos adicionais quando necessários.

- Pacotes portáteis.

- Estruturas de diretórios específicas de cada ferramenta.

- Executáveis com extensões específicas por sistema.

- Dependências nativas.

- Bibliotecas compartilhadas exigidas pelo runtime.

- Compatibilidade de ABI e libc quando aplicável.

Não instalar silenciosamente serviços, drivers, componentes de sistema ou dependências globais.

Se uma ferramenta exigir instalação privilegiada ou não puder funcionar de forma portátil, explique a limitação e ofereça um diagnóstico claro.

## 8. Integridade e segurança

Implemente as seguintes garantias:

1. HTTPS obrigatório.

2. Verificação de SHA-256 contra metadados oficiais confiáveis.

3. Verificação de assinaturas quando a fonte fornecer um mecanismo confiável.

4. Extração protegida contra path traversal, Zip Slip e links perigosos.

5. Limites razoáveis de tamanho e tratamento de arquivos malformados.

6. Instalação em diretório temporário.

7. Publicação atômica da instalação concluída.

8. Locks para evitar instalações concorrentes conflitantes.

9. Rollback em caso de falha.

10. Preservação de versões já instaladas.

11. Mensagens de erro úteis sem revelar tokens ou dados sensíveis.

Se o fornecedor não publicar checksum ou assinatura verificável, classifique explicitamente o nível de verificação disponível. Não invente uma garantia de autenticidade.

## 9. CLI uniforme

Os novos providers devem integrar-se à CLI já existente.

Exemplos desejados:

\`\`\`bash

avm providers

avm providers python

avm available python

avm available python --all

avm available python --os windows --arch x64

avm info python@3.13

avm install python@3.13

avm use python@3.13

avm current python

avm exec -- python --version

\`\`\`

Outras ferramentas:

\`\`\`bash

avm available go

avm install go@1.25

avm available dotnet

avm install dotnet@10

avm available php

avm install php@8.4

avm available ruby

avm install ruby@3.4

avm available rust

avm install rust@1.90

\`\`\`

Os números acima são exemplos de sintaxe, não uma afirmação de que essas versões estejam disponíveis. O catálogo deve determinar as versões reais.

Para providers que tenham múltiplos produtos, diferencie os produtos explicitamente. Exemplos:

\`\`\`bash

avm install dotnet-sdk@&lt;versao&gt;

avm install dotnet-runtime@&lt;versao&gt;

avm install maven@&lt;versao&gt;

avm install gradle@&lt;versao&gt;

\`\`\`

Adapte os identificadores ao padrão de nomes já adotado no AVM.

Se uma versão não existir para a plataforma solicitada, apresente as versões e alternativas compatíveis, sem tentar instalar um artefato incompatível.

## 10. Configuração por projeto

Amplie o arquivo `avm.toml` para declarar ferramentas por projeto.

Exemplo:

\`\`\`toml

[project]

name = "backend-api"

[[tools.java](http://tools.java)]

version = "21"

distribution = "temurin"

[tools.node]

version = "22.14.0"

[tools.python]

version = "3.13"

[tools.go]

version = "1.25"

[tools.dotnet]

version = "10"

product = "sdk"

[tools.php]

version = "8.4"

[tools.ruby]

version = "3.4"

[tools.rust]

version = "1.90"

channel = "stable"

\`\`\`

Essas versões são ilustrativas.

O AVM deve validar as configurações e resolver as versões somente a partir de releases disponíveis e compatíveis.

Implemente:

- Validação de configuração.

- Mensagens de erro com caminho e campo inválido.

- Resolução determinística de versões.

- Seleção de runtime por projeto.

- Execução com ambiente isolado.

- Não sobrescrever variáveis do usuário sem necessidade.

- Não modificar o ambiente do processo pai.

- Preservar argumentos, sinais e códigos de saída do processo executado.

Se uma ferramenta exigir configuração adicional, permita declarar opções específicas sem contaminar o modelo das demais linguagens.

## 11. Integração com IDEs

A arquitetura deve facilitar o uso com:

- IntelliJ IDEA.

- Visual Studio Code.

- Terminais PowerShell, CMD, Bash e Zsh.

- Scripts de build e CI/CD.

Não dependa de extensões proprietárias para instalar ou selecionar versões.

Documente como obter os caminhos dos SDKs e executáveis:

\`\`\`bash

avm path java

avm path node

avm path python

avm path go

avm path dotnet

avm path php

avm path ruby

avm path rust

\`\`\`

Quando necessário, ofereça integração por configuração do projeto, variáveis de ambiente para processos filhos ou geração de arquivos de configuração locais.

Não altere configurações de IDE automaticamente sem consentimento explícito.

## 12. Testes obrigatórios

Para cada provider, implementar:

- Testes unitários de parsing de versões.

- Testes de normalização.

- Testes de resolução de aliases.

- Testes de seleção de plataforma e arquitetura.

- Testes de metadados ausentes ou inválidos.

- Testes de checksum incorreto.

- Testes de download interrompido.

- Testes de extração segura.

- Testes de instalação e rollback.

- Testes de execução do binário.

- Testes de configuração por projeto.

- Testes de regressão para providers já existentes.

Use fixtures locais para testes unitários.

Os testes de integração devem usar artefatos oficiais e executar nos runners correspondentes quando viável.

Não faça downloads enormes em todos os testes unitários.

Não afirme que um provider está validado em Windows, macOS ou Linux se não houver evidência de testes nessa plataforma.

## 13. Implementação incremental

Não tente implementar todas as linguagens em uma única alteração gigantesca.

Siga esta ordem:

### Etapa A — Auditoria

- Inspecionar a CLI e os providers existentes.

- Identificar os contratos e módulos reutilizáveis.

- Identificar lacunas de segurança.

- Documentar incompatibilidades necessárias antes de alterá-las.

### Etapa B — Contratos

- Definir ou ajustar a abstração de provider.

- Definir os metadados comuns.

- Atualizar os schemas.

- Criar testes de contrato reutilizáveis.

### Etapa C — Primeiros providers

Implementar nesta ordem:

1. Go.

2. Python.

3. .NET SDK.

4. PHP.

5. Ruby.

6. Rust toolchain.

Priorize os providers com artefatos portáteis e fontes de metadados confiáveis.

Se um provider apresentar limitações relevantes, documente-as e avance para o próximo sem simular suporte inexistente.

### Etapa D — Catálogo

- Implementar coletores independentes.

- Adicionar validação e publicação.

- Testar falhas parciais.

- Confirmar que o catálogo anterior permanece disponível em caso de falha.

### Etapa E — Integração

- Integrar os providers à CLI.

- Integrar o arquivo `avm.toml`.

- Testar a execução de ferramentas reais.

- Validar a convivência com Java e Node.js.

### Etapa F — Documentação

Documentar instalação, comandos, plataformas, limitações, fontes, segurança e exemplos.

## 14. Critérios de aceitação

Uma linguagem só pode ser marcada como implementada quando:

- O catálogo fornece versões reais.

- As fontes e os artefatos são rastreáveis.

- A CLI consegue listar versões compatíveis.

- A instalação funciona sem privilégios de administrador, quando tecnicamente possível.

- A integridade dos artefatos é verificada conforme os mecanismos disponíveis.

- O executável instalado funciona.

- O provider integra-se ao `avm.toml`.

- Há testes automatizados.

- As limitações estão documentadas.

- A implementação não quebra Java e Node.js.

Utilize estados explícitos no catálogo ou na documentação:

- `planned`: planejado.

- `metadata`: coleta de metadados implementada.

- `experimental`: instalação parcialmente validada.

- `supported`: fluxo de instalação e execução validado.

- `unsupported-platform`: sem suporte à plataforma solicitada.

Não confunda a disponibilidade de metadados com suporte completo à instalação.

## 15. Entrega final

Ao concluir cada etapa, apresente:

1. Arquivos criados e alterados.

2. Providers implementados.

3. Fontes oficiais utilizadas.

4. Plataformas testadas.

5. Comandos que funcionam.

6. Testes executados e seus resultados reais.

7. Limitações conhecidas.

8. Riscos de segurança ainda pendentes.

9. Próxima etapa recomendada.

Comece pela auditoria do repositório e pela definição dos contratos. Depois implemente os providers Go e Python de ponta a ponta, incluindo catálogo, CLI, instalação, verificação, execução e testes.

Não entregue somente documentação ou stubs. Priorize código executável, testes reproduzíveis e compatibilidade retroativa com Java e Node.js.


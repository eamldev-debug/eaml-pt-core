ADR-007: Atestação Remota e Gestão de Chaves em Enclaves TEE (GCP Confidential Space)
​Estado: Proposto (Início do Sprint 2)
​Data: 2026-07-29
​Contexto Técnico: EAML-PT Trust Infrastructure (eIDAS 2.0 "High Assurance" & AI Act)
​Contexto e Problema
​Apesar de o repositório possuir controlos de governação rigorosos (Governance Assertions CI/CD), o ambiente de execução (runtime) numa nuvem pública apresenta vetores de ataque, como o comprometimento do hipervisor ou a extração de chaves criptográficas da memória RAM (memory dumping). Para atingir a conformidade soberana, o sistema não pode confiar implicitamente no fornecedor de cloud (GCP).
​Decisão Técnica
​O EAML-PT adotará uma arquitetura de Confidential Computing utilizando GCP Confidential Cloud Run (baseado em hardware AMD SEV-SNP) combinado com GCP Attestation Service e Cloud HSM.
​O fluxo de atestação obrigatório será o seguinte:
​Isolamento em Enclave (TEE): O binário do EAML-PT corre dentro de um Trusted Execution Environment (TEE), onde a RAM é encriptada ao nível do hardware (chaves cravadas no processador AMD, inacessíveis à Google).
​Medição de Inicialização (Golden Measurement): Durante o arranque, o hardware mede o hash criptográfico do SO e do contentor do EAML-PT.
​Atestação Remota: O enclave solicita um Attestation Token (OIDC) ao GCP Attestation Service, assinando digitalmente as medições de hardware.
​Libertação Condicional de Chaves (Key Release): O EAML-PT apresenta o token ao Cloud HSM. As chaves operacionais (incluindo as chaves pós-quânticas ML-KEM-768) só são libertadas se o token provar que o hash do contentor corresponde exatamente à versão "Fast Track Approved" no CI/CD.
​Políticas de Segurança (Zero-Storage & HNDL)
​Sem disco persistente: A montagem de volumes será estritamente desativada. Toda a manipulação de chaves ocorre na RAM encriptada pelo AMD SEV-SNP.
​Higiene de Memória Volátil: Após a assinatura ou verificação de um evento no barramento (Kafka), as variáveis que contêm chaves criptográficas em memória sofrem zeroization imediata.
​Consequências
​Positivas: Previne ameaças internas (ex: administradores da Cloud não conseguem aceder a dados) e ataques HNDL, garantindo o Nível de Garantia "Elevado" do eIDAS 2.0.
​Negativas: Adiciona ligeira complexidade ao processo de Cold Start devido ao tempo necessário para o handshake de atestação com o HSM.

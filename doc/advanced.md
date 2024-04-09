Limitações da API export comments:
- 5 requisições por segundo;
- Até 5 requisições processando em um dado momento;
- 5 requisições na fila para processamento. Depois disso, a requisição é ignorada e recebemos um código 429 de retorno.

Para exportar comentários, a API suporta somente URLs para posts. Não podemos usá-la com hashtags ou similares, embora ela também suporte extrair essas URLs a partir de hashtags para algumas redes, como uma funcionalidade adicional:
- [Instagram](https://exportcomments.com/export-instagram-hashtags)
- [TikTok](https://exportcomments.com/download-tiktok-hashtags)
- [Twitter](https://exportcomments.com/export-twitter-followers)

Mas o foco deste documento é maximizar a extração de downloads de comentários, supondo que já temos os links para posts.

O programa será dividido em várias partes, pois o processamento é feito em servidor deles.


# Busca de posts por tópicos

Este programa é responsável pela busca de posts a serem exportados. Ao usar a API com uma URL de tópicos (_hashtags_, ou qualquer equivalente), ela nos retorna uma lista de URLs de posts. O programa deve enviar essas URLs para uma fila de mensagens (MQ) dedicada para tópicos, para que o programa de coleta possa processá-las como se fosse uma URL normal.

A entrada e o comportamento desse programa pode ser qualquer coisa para facilitar o uso pelo projeto. Por exemplo, ela pode receber uma lista de tópicos e uma rede social, contruir as URLs a partir disso, ou só a lista e tópicos e construir a URL para todas as redes que sabemos como fazer isso, etc. Isso do uso do programa pelo projeto.

# Coleta

## Enviar URL para processamento

Lê de uma fila de mensagens (Message Queue, MQ) dedicada para a rede, por exemplo [RabbitMQ](https://www.rabbitmq.com/), os links para posts a serem processados e os envia para a API export comments usando a [biblioteca desenvolvida por eles](https://github.com/exportcomments/exportcomments-python) para iniciar um serviço de exportação de comentários para a URL recebida. Bem simples. O programa deve aceitar a lita de canais a ser subscrito. Ao receber a mensagem, deve enviar para a API export comments, e caso ela venha de uma lista para tópicos, anotar ela em um banco Key-Value (KV), por exemplo o [KeyDB](https://docs.keydb.dev/) (evite Redis pois ele se tornou código proprietário), deve ser armazenado o GUID retornado pela API e a rede social originária dele (o nome da fila).

## Download de resultados

Este programa é responsável por receber uma requisição web (webhook) que indica que o download está pronto para ser realizado. Isso requer uma infraestrutura para receber requisições da internet (usar [SSH tunnels](https://www.ssh.com/academy/ssh/tunneling-example#local-forwarding) para testar na máquina em cloud). Ele inicia um novo processo ([multiprocessing](https://docs.python.org/3/library/multiprocessing.html#multiprocessing.Process)) para fazer o download JSON dele e inserir no banco MongoDB, ou caso a fila de origem (recuperado com o GUID no banco KV mencionado no passo anterior) seja uma fila de tópicos, deve-se já gerar as URLs a partir do JSON e enviar para a fila de mensagens dedicada para a rede social.

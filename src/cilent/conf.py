class ClientConfig:
    G_PAIRING_PORT = 10080  # <本机端口> 接收来自服务器的配对广播 & 承载配对流程
    G_MASSAGE_RECV_PORT = 22218  # <本机端口> 用于接收来自服务器的包
    G_MASSAGE_SEND_PORT = 30141  # <本机端口> 用于向服务器发送包
    G_SERVER_MASSAGE_ADDR = None  # <服务器地址> 服务器的收包地址

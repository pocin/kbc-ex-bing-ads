from keboola import docker

def parse_config(datadir):
    cfg = docker.Config(datadir)
    return cfg.get_parameters()

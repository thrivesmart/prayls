import yaml

class LilConfig:
  
  "The config attribute, which much be initialized by calling load in your app's main function"
  config = {}

  @staticmethod
  def Load():
    """Returns the parsing of production.yaml or development.yaml"""
    conf = yaml.load(file('config/production.yaml','r'))
    
    # load development config and override production options
    try:
        conf.update(yaml.load(file('config/development.yaml','r')))
    except IOError:
        pass
    
    LilConfig.config.update(conf)
    return conf
    
  

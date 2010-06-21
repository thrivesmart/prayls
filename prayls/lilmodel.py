from google.appengine.ext import db

class LilModel:

  # This should always be used as close to a put() as possible to avoid race conditions
  @staticmethod
  def UniqueValue(entity, property_name):
    table = entity.__class__.__name__
    value = getattr(entity, property_name)
    if entity.is_saved():
      return db.GqlQuery("SELECT __key__ FROM "+table+" WHERE "+property_name+" = :1 AND __key__ != :2", value, entity.key()).get() == None
    else:
      return db.GqlQuery("SELECT __key__ FROM "+table+" WHERE "+property_name+" = :1", value).get() == None


  # Takes an entity and returns the hash of strings that represents that entity, useful for json-ificiation
  # If properties == None, it will return all properties.  Otherwise it will use only ouput the properties listed.
  @staticmethod
  def ToHash(entity, properties=None):
    result = {'__key__': str(entity.key())}
    if properties == None:
      properties = entity.__class__.properties()
    for prop in properties:     
      val = getattr(entity, prop)
      if isinstance(val, db.Model):
        result[prop] = str(val.key())
      else:
        result[prop] = str(val)
        
    return result
  
  # Takes an array of entities and returns the hash of strings that represents that array, useful for json-ificiation
  @staticmethod
  def MapToHash(entity_array, properties=None):
    return map(lambda entity: LilModel.ToHash(entity, properties), entity_array)
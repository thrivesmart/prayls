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

  @staticmethod
  def ToHash(entity):
    result = {'__key__': str(entity.key())}
    for prop in entity.__class__.properties():
      result[prop] = str(getattr(entity, prop))
    return result
  
  @staticmethod
  def MapToHash(entity_array):
    return map(lambda entity: LilModel.ToHash(entity), entity_array)
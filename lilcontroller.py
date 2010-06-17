import os
from google.appengine.ext.webapp import template

class LilController:

  @staticmethod
  def Render(controller, view, layout = None, view_locals = {}, layout_locals = {}):
    view_path = os.path.join(os.path.dirname(__file__), '../../app/views/'+controller+'/'+view+'.html')
    main_content = template.render(view_path, view_locals)
    
    if layout != None:
      layout_path = os.path.join(os.path.dirname(__file__), '../../app/views/layouts/'+layout+'.html')
      if 'body' not in layout_locals:
        layout_locals['body'] = {'main': ''}
      layout_locals['body']['main'] = main_content
      main_content = template.render(layout_path, layout_locals)
    
    return main_content

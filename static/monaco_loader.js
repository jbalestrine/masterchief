// Lightweight Monaco loader using jsDelivr
(function(window){
  function loadScript(url, cb){
    var s=document.createElement('script'); s.src=url; s.onload=cb; document.head.appendChild(s);
  }
  function create(settings){
    if(window.monaco && window.monaco.editor){
      settings.onLoad && settings.onLoad(window.monaco);
      return;
    }
    // load AMD loader
    loadScript('https://cdn.jsdelivr.net/npm/monaco-editor@0.39.0/min/vs/loader.js', function(){
      require.config({ paths: { 'vs': 'https://cdn.jsdelivr.net/npm/monaco-editor@0.39.0/min/vs' } });
      require(['vs/editor/editor.main'], function(){
        settings.onLoad && settings.onLoad(window.monaco);
      });
    });
  }
  function createEditor(containerId, initialValue, language, options){
    options = options || {};
    create({onLoad:function(monaco){
      var container=document.getElementById(containerId);
      if(!container) return;
      container.innerHTML='';
      var editor = monaco.editor.create(container, Object.assign({value: initialValue || '', language: language || 'plaintext', automaticLayout: true}, options));
      // expose save helper
      return editor;
    }});
  }
  window.MonacoLoader = {
    load: create,
    createEditor: createEditor
  };
})(window);

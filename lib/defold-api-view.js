var WebEditorView;

module.exports = WebEditorView = (function () {
  function WebEditorView(serializedState) {
    var self;
    this.element = document.createElement("iframe");
    this.relocate("http://localhost:3000/");
    this.element.setAttribute("name", "disable-x-frame-options");
    self = this;
  }

  WebEditorView.prototype.relocate = function (source) {
    if (this.element.contentWindow) {
      return (this.element.contentWindow.location.href = source);
    } else {
      return this.element.setAttribute("src", source);
    }
  };

  WebEditorView.prototype.getTitle = function () {
    return this.title || "Defold API Reference";
  };

  WebEditorView.prototype.serialize = function () {
    if (this.element.contentWindow) {
      return this.element.contentWindow.location.href;
    } else {
      return this.element.getAttribute("src");
    }
  };

  WebEditorView.prototype.destroy = function () {
    return this.element.remove();
  };

  WebEditorView.prototype.getElement = function () {
    return this.element;
  };

  return WebEditorView;
})();

var CompositeDisposable, allowUnsafeEval, WebEditorView, path, url;
CompositeDisposable = require("atom").CompositeDisposable;
allowUnsafeEval = require("loophole").allowUnsafeEval;
WebEditorView = require("./defold-api-view");
path = require("path");
url = require("url");
const http = require('http');
const handler = require('serve-handler');
const www = path.join(atom.packages.resolvePackagePath("defold-api"), "defold/");
const server = http.createServer((request, response) => {
  return handler(request, response, {"public": www});
})

module.exports = {
  activate: function () {
    var pane, paneElement, subscription;
    this.disposable = new CompositeDisposable();
    pane = atom.workspace.getActivePane();
    paneElement = atom.views.getView(pane);
    subscription = atom.commands.add("atom-workspace", {
      "defold-api:open": (function (_this) {
        return function () {
          return _this.open();
        };
      })(this),
      "defold-api:reload": (function (_this) {
        return function () {
          return _this.reload();
        };
      })(this),
    });
    this.disposable.add(
      atom.workspace.addOpener(function (uri) {
        if (uri === "view://defold-api") {
          return new WebEditorView();
        }
      })
    );
    this.disposable.add(atom.views.addViewProvider(WebEditorView, paneElement));
    return this.disposable.add(subscription);
  },
  deactivate: function () {
    var _ref;
    this.disposable.dispose();
    this.subscriptions.dispose();
    return (_ref = this.toolBar) != null ? _ref.removeItems() : void 0;
  },
  reload: function () {
    var pane;
    pane = atom.workspace.getActivePane();
    if (pane.activeItem instanceof WebEditorView) {
      return pane.activeItem.element.contentWindow.location.reload();
    }
  },
  open: function () {
    var pane;
    if (!server.listening) {
      this.startServer();
    }
    return (pane = atom.workspace.open("view://defold-api", {
      split: "right",
    }));
  },
  startServer: function () {
    return allowUnsafeEval(function () {
      return server.listen(3000, () => {
        console.log('Running at http://localhost:3000');
      });
    });
  },
  consumeToolBar: function (toolBar) {
    this.toolBar = toolBar("defold-api");
    this.toolBar.addSpacer();
    return this.toolBar.addButton({
      icon: "book-open",
      iconset: "mdi",
      callback: "defold-api:open",
      tooltip: "Open Defold API",
    });
  },
};

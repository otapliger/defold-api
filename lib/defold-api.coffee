# atom clean up work
{CompositeDisposable} = require 'atom'
{allowUnsafeEval} = require 'loophole'

# included modules
path = require 'path'
WebEditorView = require './defold-api-view'
liveServer =  allowUnsafeEval -> require "live-server"
url = require 'url'

module.exports =
	activate: (state) ->
		@disposable = new CompositeDisposable()
		pane = atom.workspace.getActivePane()
		paneElement = atom.views.getView(pane)
		subscription = atom.commands.add 'atom-workspace',
			'defold-api:open': => @open()
			'defold-api:reload': => @reload()
		@disposable.add atom.workspace.addOpener (uri) ->
			return new WebEditorView() if uri is "view://defold-api"
		@disposable.add atom.views.addViewProvider WebEditorView, paneElement
		@disposable.add subscription

	# TODO: about window

	deactivate: ->
		@disposable.dispose()
		@subscriptions.dispose()
		@toolBar?.removeItems()

	reload: (event) ->
		pane = atom.workspace.getActivePane()
		if pane.activeItem instanceof WebEditorView
			pane.activeItem.element.contentWindow.location.reload()

	open: ->
		@startServer()
		pane = atom.workspace.open("view://defold-api", split: 'right')

	getPaths: ->
		packagePath = atom.packages.getActivePackage('defold-api').path
		systemPath = path.join(packagePath, 'defold')
		return systemPath

	startServer: (port) ->
		projectPath = @getPaths()

		params = {
			port: 4000,
			root: projectPath,
			open: false,
			file: "index.html"
		};

		allowUnsafeEval -> liveServer.start params;

	consumeToolBar: (toolBar) ->
		@toolBar = toolBar "defold-api"

		# TOOLBAR - OPEN FILE
		@toolBar.addSpacer()
		@toolBar.addButton
			icon: "book-open"
			iconset: "mdi"
			callback: "defold-api:open"
			tooltip: "Open Defold API"

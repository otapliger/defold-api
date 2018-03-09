module.exports =
class WebEditorView
	constructor: (serializedState) ->
		@element = document.createElement 'iframe'
		@relocate 'http://127.0.0.1:4000/'
		@element.setAttribute 'name', 'disable-x-frame-options'
		self = this

	relocate: (source) ->
		if (@element.contentWindow)
			@element.contentWindow.location.href = source
		else
			@element.setAttribute('src', source)

	getTitle: () ->
		return @title || 'Defold API Reference'

	serialize: ->
		if @element.contentWindow
			return @element.contentWindow.location.href
		else
			return @element.getAttribute('src')

	destroy: ->
		@element.remove()

	getElement: ->
		@element

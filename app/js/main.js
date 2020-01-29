import './underscore.js';
import './backbone.js';

(function (_window, _document, _HTMLDocument) {
	var main = {};

	main.SwissTurnier = function () {
		var me =  this;
		me.context = 'Text';
	};

	main.SwissTurnier.prototype.get_context = function () {
		var me = this;
		return me.context;
	};


	HTMLDocument.prototype.ready = function () {
		return new Promise(function(resolve, reject) {
			if (_document.readyState === 'complete') {
				resolve(_document);
			} else {
				_document.addEventListener('DOMContentLoaded', function() {
				resolve(_document);
			});
						}
		});
	}
	_document.ready().then(function (doc) {
		//console.log('The anchor:', doc.getElementById('anchor1'));
		doc.getElementById('anchor1').innerHTML = '<em>Hello World</em>';
	});

	return main;
}(window, document, HTMLDocument));

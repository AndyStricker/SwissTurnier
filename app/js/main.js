import './underscore.js';
import './backbone.js';  // requires Zepto for Ajax

(function (_window, _document, _HTMLDocument) {
	var main = {
		'API_PREFIX': '/v1',
	};

	main.SwissTurnier = function () {
		var me =  this;
		me.context = 'Text';
	};

	main.SwissTurnier.prototype.get_context = function () {
		var me = this;
		return me.context;
	};

	main.makeAPI = function (url) {
		return main.API_PREFIX + url;
	};

	/* Data Models */

	main.Categories = Backbone.Collection.extend({
		urlRoot: '/categories',
		url: '/category',
		parse: (data) => { return data.items; }
	});

	main.Teams = Backbone.Collection.extend({
		urlRoot: main.makeAPI('/teams'),
		url: main.makeAPI('/team'),
		parse: (data) => { return data.items; }
	});

	main.PlayRounds = Backbone.Collection.extend({
		url: main.makeAPI('/playround'),
	});

	main.PlayRound = Backbone.Collection.extend({
		url: main.makeAPI('/playround/1'),
		parse: (data) => { return data.plays; }
	});

	/* Views */

	main.PlayView = Backbone.View.extend({
		tagName: 'tr',
		className: 'play',
		template: _.template($('#play-view-tmpl').html()),

		initialize: function() {
			//this.listenTo(this.model, 'sync change', this.render);
		},

		render: function() {
			var html = this.template(this.model.toJSON());
			this.$el.html(html);
			return this;
		},
	});


	main.PlayRoundListView = Backbone.View.extend({
		el: '#playround-view',

		initialize: function() {
			this.listenTo(this.collection, 'sync', this.render);
		},

		render: function() {
			var $list = this.$('tbody.playround-list').empty();

			this.collection.each(function(model) {
				var item = new main.PlayView({model: model});
				$list.append(item.render().$el);
			}, this);

			return this;
		},

		events: {
			'click .create': 'onCreate'
		},

		onCreate: function() { }
	});

	/* Main part with on ready handler */

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
		var playRounds = new main.PlayRound();
		var playRoundView = new main.PlayRoundListView({collection: playRounds});
		playRounds.fetch();
	});

	return main;
}(window, document, HTMLDocument));

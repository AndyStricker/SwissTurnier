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

	/* Data Models */

	main.Categories = Backbone.Collection.extend({
		urlRoot: '/categories',
		url: '/category',
		parse: (data) => { return data.items; }
	});

	main.Teams = Backbone.Collection.extend({
		urlRoot: '/teams',
		url: '/team',
		parse: (data) => { return data.items; }
	});

	main.PlayRounds = Backbone.Collection.extend({
		url: '/playround',
	});

	main.PlayRound = Backbone.Collection.extend({
		url: '/playround/1',
	});

	/* Views */

	main.PlayView = Backbone.View.extend({
		tagName: 'li',
		className: 'play',

		initialize: function() {
			//this.listenTo(this.model, 'sync change', this.render);
		},

		render: function() {
			//var html = this.template(this.model.toJSON());
			var html =
				'<p>Team A: ' + this.model.get('id_team_a') + ' points: ' + this.model.get('points_a') + '</p>' +
				'<p>Team B: ' + this.model.get('id_team_b') + ' points: ' + this.model.get('points_b') + '</p>';
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
			var $list = this.$('ul.playround-list').empty();

			this.collection.each(function(model) {
				var item = new PlayRoundView({model: model});
				$list.append(item.render().$el);
			}, this);

			return this;
		},

		events: {
			'click .create': 'onCreate'
		},

		onCreate: function() { }
	});


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
		doc.getElementById('anchor1').innerHTML = '<em>Started up</em>';

		var playRounds = new main.PlayRound();
		var playRoundView = new main.PlayRoundListView({collection: playRounds});
		playRounds.fetch();
	});

	return main;
}(window, document, HTMLDocument));

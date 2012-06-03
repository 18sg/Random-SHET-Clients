request = require("q-http").read

matches = [
	[/step1-selected/, {name: "placed", final: false}],
	[/step2-selected/, {name: "preparing", final: false}],
	[/step3-selected/, {name: "oven", final: false}],
	[/step4-selected/, {name: "QC", final: false}],
	[/step5-delivery-selected/, {name: "delivery", final: false}],
	[/step5-delivery-past/, {name: "delivered", final: true}]
]


class PizzaTracker
	constructor: (@path, @shet) ->
		@shet.add_action @path + "track_pizza", @track_pizza
		@shet.add_action @path + "latest", => @latest
	
	track_pizza: (id) =>
		new Pizza(this, id)
		@latest = @path + "pizzas/" + id


# An individual pizza being tracked.
class Pizza
	constructor: (@parent, @id) ->
		@shet = @parent.shet
		@state = null
		
		# Full path for a node associated with this pizza.
		node_name = (name) => "#{@parent.path}pizzas/#{@id}/#{name}"
		
		@state_change_event = @shet.add_event node_name "on_state_change"
		
		@events = {}
		for [_, {name}] in matches
			@events[name] = @shet.add_event node_name "on_#{name}"
		
		@shet.add_action node_name("get_state"), => @state.name
		
		# Start the update cycle.
		@update_state()
	
	# Get the current pizza state in a deferred.
	get_state: =>
		url = "http://www.dominos.co.uk/checkout/pizzaTrackeriFrame.aspx?id=#{@id}"
		request(url).then (body) ->
			body = body.toString()
			for [regex, name] in matches
				if body.match regex
					return name
	
	# Update the current state every 5 seconds until we reach a final state.
	update_state: =>
		@get_state().then (state) =>
			if @state != state
				@state = state
				@state_changed state
				unless state.final
					setTimeout @update_state, 5000
		.end()
	
	# Called when the state changes.
	state_changed: (state) =>
		@state_change_event.raise state.name
		@events[state.name].raise state.name


path = process.argv[2]
shet = require("shet-client").connect()
new PizzaTracker path, shet

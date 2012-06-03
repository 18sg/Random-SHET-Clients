Domino's Pizza Tracker
======================

Track the status of a pizza from SHET!

Dependencies
------------

- node
- CoffeeScript `# npm install -g coffee-script`
- shet-client `$ npm install shet-client`
- q-http `$ npm install q-http`

Running
-------

```
coffee pizza.coffee /pizza/
```

Where `/pizza/` is the directory to put everything in.

Example usage (where ODYzN... is the id from the tracking page URL):

```
$ shet /pizza/track_pizza ODYzNzEyODY2NDQxODI4NTY3
"/pizza/pizzas/ODYzNzEyODY2NDQxODI4NTY3"
$ shet /pizza/pizzas/ODYzNzEyODY2NDQxODI4NTY3/get_state
"preparing"
$ shet /pizza/pizzas/ODYzNzEyODY2NDQxODI4NTY3/on_delivery
  ...some time later...
[ "delivery" ]
```

Winning!

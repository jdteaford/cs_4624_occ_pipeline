<template>
	{% for key,value in form_data.items() %}
	<h2> {{key}}</h2>
	<p> {{value}}</p>
	{% endfor %}
</template>

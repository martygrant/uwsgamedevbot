import discord
from discord.ext import commands
from weather import Weather as w, Unit
import utilities as utils
from datetime import datetime, timedelta

class Weather(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.weather_object = w(unit=Unit.CELSIUS)
		self.degree_sign = u'\N{DEGREE SIGN}'

	@commands.command()
	async def weather(self, ctx):
		"""Get current weather conditions at a specified location from Yahoo. E.g '!weather glasgow'"""

		# Default to glasgow if no argument passed
		if not ctx.args:
			city = 'glasgow'
		else:
			city = ctx.args[0]

		location = self.weather_object.lookup_by_location(city)

		embed = discord.Embed(type="rich", colour=utils.generate_random_colour(), timestamp=datetime.now())
		embed.set_author(name=location.title)
		embed.add_field(name="Temperature", value="{}{}{}".format(location.condition.temp, self.degree_sign, location.units.temperature))
		embed.add_field(name="Condition", value=location.condition.text)
		embed.add_field(name="Humidity", value="{}%".format(location.atmosphere["humidity"]))
		embed.add_field(name="Wind", value="{} {}".format(location.wind.speed, location.units.speed))

		await ctx.message.channel.send(embed=embed)

	@commands.command()
	async def forecast(self, ctx):
		"""Get the forecast for the next 5 days for a specified location from Yahoo. E.g '!forecast glasgow'"""

		# Default to glasgow if no argument passed
		if not ctx.args:
			city = 'glasgow'
		else:
			city = ctx.args[0]

		location = self.weather_object.lookup_by_location(city)
		forecasts = location.forecast
		embed = discord.Embed(type="rich", colour=utils.generate_random_colour(), timestamp=datetime.now())
		embed.set_author(name="5-day forecast for {}".format(location.title))

		count = 0
		for cast in forecasts:
			if count > 4:
				break
			count += 1
			embed.add_field(name=cast.date, value="{}\nHigh: {}{}{}\nLow: {}{}{}".format(cast.text, cast.high, self.degree_sign, location.units.temperature, cast.low, self.degree_sign, location.units.temperature))

		await ctx.message.channel.send(embed=embed)

def setup(bot):
	bot.add_cog(Weather(bot))
	print("Weather module loaded.")

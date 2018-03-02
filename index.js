const Discord = require("discord.js")
, fs = require("fs-extra")
, join = require("path").join;

global.dClient = new Discord.Client();
dClient.version = process.env.version;
dClient.github = "https://github.com/martygrant/uwsgamedevbot/tree/node";
dClient.soc = {
    logo: "https://cdn.discordapp.com/icons/405451738804518916/03b9c866123fa1de250f462e5f7920b8.png"
};

dClient.config = require(join(__dirname, "lib", "config.json"));
dClient.commands = require(join(__dirname, "lib", "commands.json"));

dClient.lib = {
    handlers: {},
    commands: {}
};

// import handlers
const handlerPath = join(__dirname, "lib", "handlers");
for (let handler of fs.readdirSync(handlerPath))
{
    dClient.lib.handlers[handler.replace(".js", "")] = require(join(handlerPath, handler));
}

// import commands
const commandPath = join(__dirname, "lib", "commands");
for (let command of fs.readdirSync(commandPath))
{
    dClient.lib.commands[command.replace(".js", "")] = require(join(commandPath, command));
}

console.log(dClient.lib.handlers.ready);

dClient.once("ready", dClient.lib.handlers.ready);
dClient.login(process.env.token)
    .catch(console.error);

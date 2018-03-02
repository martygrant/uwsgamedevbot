const Discord = require("discord.js");

function help(msg)
{
    let embed = new Discord.MessageEmbed()
        .setAuthor(dClient.user.username, dClient.user.displayAvatarURL(), dClient.github)
        .setTimestamp(msg.createdAt)
        .setFooter("UWS Game Dev Society", dClient.soc.logo);

    if (!msg.args || !msg.args.length)
    {
        embed.setDescription("This is a list of available commands.");

        for (const cmd in dClient.commands)
            embed.addField(cmd, dClient.commands[cmd].description, true);

        embed.addField("\u200b", `To get help on a specific command, type \`\`\`\n${dClient.config.prefix}help [command]\`\`\``);
    }

    else
    {
        let requestedCommand = msg.args[0].toLowerCase();
        if (Object.keys(dClient.commands).includes(requestedCommand) || Object.values(dClient.commands).some(obj => obj.alias.includes(requestedCommand)))
        {
            let commandObj;
            if (Object.keys(dClient.commands).includes(requestedCommand)) commandObj = dClient.commands[requestedCommand];
            else
            {
                for (const cObj of Object.values(dClient.commands))
                {
                    if (cObj.alias.includes(requestedCommand))
                    {
                        commandObj = cObj;
                        break;
                    }
                }
            }

            embed.setTitle(requestedCommand)
                .setDescription(commandObj.description)
                .addField("Alias", `\`${commandObj.alias.join("`, `")}\``);

            for (const arg in commandObj.arguments)
            {
                let argumentObj = commandObj.arguments[arg];
                embed.addField(arg + ((argumentObj.optional) ? "*" : ""), `${argumentObj.description}`);
            }

            embed.addField("Command Usage:", `\`\`\`\n${dClient.config.prefix}${requestedCommand} ${commandObj.syntax}\`\`\``);
        }

        else
        {
            msg.args = null;
            return help(msg);
        }
    }

    return msg.channel.send({ embed }).catch(console.error);
}

module.exports = help;

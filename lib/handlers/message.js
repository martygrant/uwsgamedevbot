const Discord = require("discord.js");

function getPermLevel(member)
{
    if (!(member instanceof Discord.GuildMember)) return 100;

    if (member.id === member.guild.owner.id) return 300;
    else if (member.permissions.serialize()["ADMINISTRATOR"]) return 200;
    else return 100;
}

function message(msg)
{
    let consoleOutput = "\n" + new Date().toUTCString() + "\n";
    consoleOutput += `@${msg.author.username}: "${msg.content}"\n`;
    consoleOutput += `[${msg.guild.name}] #${msg.channel.name}`;

    console.log(consoleOutput);

    // ignore bot users
    if (msg.author.bot) return;

    let splitMsg = msg.content.split(" ");
    msg.command = null;
    msg.args = null;

    // check whether user is using command prefix or mention to execute a command, and assign them to 'msg' accordingly
    if (msg.mentions.users.has(dClient.user.id) && splitMsg[0].includes(dClient.user.id) && splitMsg.length > 1)
    {
        msg.command = splitMsg[1].toLowerCase();
        msg.args = splitMsg.slice(2);
    }

    else if (splitMsg[0].startsWith(dClient.config.prefix))
    {
        msg.command = splitMsg[0].slice(dClient.config.prefix.length).toLowerCase();
        msg.args = splitMsg.slice(1);
    }

    if (msg.command)
    {
        for (const cmd in dClient.commands)
        {
            for (const alias of dClient.commands[cmd].alias)
            {
                if (msg.command === alias)
                {
                    if (getPermLevel(msg.member || msg.author) >= dClient.commands[cmd].permissions)
                    {
                        try
                        {
                            // execute the command module
                            return dClient.lib.commands[cmd](msg);
                        }

                        catch (err)
                        {
                            // catch an error in case the command module is faulty
                            console.error(err);
                            msg.reply(`If this keeps happening, submit an issue at ${dClient.github}.\n\`\`\`js\n${err.message}\`\`\``).catch(console.error);
                        }
                    }
                }
            }
        }
    }
}

module.exports = message;

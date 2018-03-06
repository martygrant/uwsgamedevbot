function say(msg)
{
    if (!msg.args || !msg.args.length) return msg.reply("Something.").catch(console.error);

    return msg.reply(msg.args.join(" ")).catch(console.error);
}

module.exports = say;

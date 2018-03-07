function dice(msg)
{
    let sides = 6;
    if (msg.args.length && !Number.isNaN(msg.args[0])) sides = parseInt(msg.args[0]);

    return msg.channel.send(Math.floor(Math.random() * sides + 1), { code: "js" }).catch(console.error);
}

module.exports = dice;

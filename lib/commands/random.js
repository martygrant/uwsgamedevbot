function random(msg)
{
    let min = 0
    , max = Number.MAX_SAFE_INTEGER - 1
    , randomNumber = Math.random();

    if (msg.args.length === 1)
    {
        max = msg.args[0];
        if (Number.isNaN(max)) return msg.reply("Your argument must be a number. Try again.").catch(console.error);
    }

    else if (msg.args.length === 2)
    {
        min = msg.args[0];
        max = msg.args[1];

        if (Number.isNaN(min) || Number.isNaN(max)) return msg.reply("Your arguments must be numbers. Try again.").catch(console.error);
    }

    min = parseInt(min);
    max = parseInt(max);

    return msg.channel.send(Math.floor(randomNumber * (max - min + 1)) + min, { code: "js" }).catch(console.error);
}

module.exports = random;

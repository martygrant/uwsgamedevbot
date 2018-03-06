function version(msg)
{
    return msg.reply(`v${dClient.version} - ${dClient.github}`).catch(console.error);
}

module.exports = version;

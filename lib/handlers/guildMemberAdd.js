function guildMemberAdd(member)
{
    let lobbyChannel = dClient.channels.get("412327350366240768");
    let rulesChannel = dClient.channels.get("405741154643214356");
    let announcementChannel = dClient.channels.get("405451914973806602");
    let introductionChannel = dClient.channels.get("413835267557031937");

    lobbyChannel.send(`Welcome ${member.toString()} to the UWS Game Dev Society!\n\nPlease check out ${rulesChannel.toString()} and set your server nickname to your real name.\nVisit ${announcementChannel.toString()} to see what events are coming up! Why not also ${introductionChannel.toString()}?\n\nPlease conduct yourself professionally in public-facing channels like ${lobbyChannel.toString()}. Thanks!`).catch(console.error);
}

module.exports = guildMemberAdd;

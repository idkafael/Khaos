"""
Constants for custom emojis used throughout the bot
Copy the IDs from ?get_emotes command output
"""

EMOJI_IDS = {
    "adminicon": 1432030962207953016,
    "adminpurple1": 1432030881396162600,  # Renamed to avoid duplicate key
    "adminpurple2": 1432030886555156630,  # Renamed to avoid duplicate key
    "adminpurple3": 1432030931199197307,  # Renamed to avoid duplicate key
    "boost": 1432030907698774239,
    "butterfliespurple": 1432031759788412991,
    "crown": 1432030923494260747,
    "kittylaptop": 1432031793955213487,
    "lightpurplecheck": 1432030912140279868,
    "memberpurple": 1432030891542315169,
    "memberspurple": 1432030897015754772,
    "modbadgepurple": 1432030919845220432,
    "olebot": 1432030921703559298,
    "ownershipneon": 1432030964111904788,
    "pastelstaff": 1432030938878972066,
    "pinkheart": 1432031755484794942,
    "pinkstaffbadge": 1432030944935805159,
    "purplearrow1": 1432031776599052370,  # Renamed to avoid duplicate key
    "purplearrow2": 1432031804470329415,  # Renamed to avoid duplicate key
    "purplebutterflies": 1432031769166741668,
    "purplecheck": 1432031763378471034,
    "purpleclouds": 1432031753739964588,
    "purpledot": 1432030924828049559,
    "purpleenvelope": 1432031787881861180,
    "purpleheart": 1432031750577717350,
    "purplemodbadge": 1432030927269400647,
    "purplerollingstar": 1432031780646424586,
    "purplesparkles": 1432031757414305922,
    "purplestaffbadge": 1432030884621717644,
    "purplestar": 1432031747792699482,
    "purpleverifed": 1432030882851590315,
    "purpleverification": 1432031785792962601,
    "purpleverified": 1432030909552656595,
    "serverboosterpurple": 1432030960358260827,
    "shinypurplemoderator": 1432030917911773184,
    "shinypurplestaff": 1432030943111024660,
    "staff": 1432030905693765662,
    "stafficonpurple": 1432030893006000169,
    "star": 1432031761604542616,
    "streamer": 1432030954972647444,
    "verifiedpurple1": 1432030888966750328,  # Renamed to avoid duplicate key
    "verifiedpurple2": 1432030935167143936,  # Renamed to avoid duplicate key
    "violetsmalldot": 1432030895086239974,
}


def get_emoji(emoji_name: str) -> str:
    """
    Get emoji string for use in Discord
    
    Args:
        emoji_name: Name of the emoji from EMOJI_IDS
        
    Returns:
        String in format <:name:id> for the emoji
    """
    if emoji_name not in EMOJI_IDS:
        return "❓"  # Fallback emoji
    
    return f"<:{emoji_name}:{EMOJI_IDS[emoji_name]}>"


def get_emoji_partial(emoji_name: str):
    """
    Get PartialEmoji object for use in SelectOption and Button
    
    Args:
        emoji_name: Name of the emoji from EMOJI_IDS
        
    Returns:
        String representation of the emoji (Discord will handle it automatically)
    """
    if emoji_name not in EMOJI_IDS:
        return None  # Return None to use default
    
    return str(EMOJI_IDS[emoji_name])  # Just the ID as string

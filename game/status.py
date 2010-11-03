bads = set(["blind", "lycanthropy", "stoning", "injured leg"])
goods = set(["fast", "very fast", "stealth"])

def type(status):
    if status in bads:
        return "bad"
    elif status in goods:
        return "good"
    else:
        return "neutral"

messages = {
    "blind": {
        "You are blinded by a blast of light!": True,
        "You can see again.": False
    },
    "lycanthropy": {
        "You feel feverish.": True,
        "You feel purified.": False
    },
    "fast": {
        "You feel quick!": True,
        "You seem faster.": True,
        "You speed up.": True,
        "Your quickness feels more natural.": True, 
        "\"and thus I grant thee the gift of Speed!\"": True,
        "You are slowing down.": False,
        "You feel slow!": False,
        "You feel slower.": False,
        "You seem slower.": False,
        "You slow down.": False,
        "Your limbs are getting oozy.": False,
        "Your quickness feels less natural.": False
    },
    "very fast": {
        "You are suddenly moving faster.": True,
        "You are suddenly moving much faster.": True,
        "Your knees seem more flexible now.": True,
        "Your .* get new energy.": True,
        "You feel yourself slowing down a bit.": False,
        "You feel yourself slowing down.": False,
        "You slow down.": False,
        "Your quickness feels less natural.": False,
    },
    "stealth": {
        "You feel stealthy!": True,
        "\"and thus I grant thee the gift of Stealth!\"": True,
        "You feel less stealthy!": False
    },
    "teleportitis": {
        "You feel diffuse.": True,
        "You feel very jumpy.": True,
        "You feel less jumpy.": False
    },
    "stoning": {
        "You are slowing down.": True, 
        "Your limbs are stiffening.": True,
        "You feel limber!": False,
        "You feel more limber.": False,
        "What a pity - you just ruined a future piece of": False
    },
    "injured leg": {
        "Your right leg is in no shape for kicking.": True,
        "Your (legs)? (feels)? somewhat better.": False
    },
    "levitating": {
        "You are floating high above the fountain.": True,
        "You are floating high above the stairs.": True,
        "You cannot reach the ground.": True,
        "You have nothing to brace yourself against.": True,
        "You start to float in the air!": True,
        "You float gently to the floor.": False,
    }
}

ibm = dict( 
    zip(
    (ord(code_point) for code_point in
        # Normal IBMgraphics...
        u'\u2502\u2500\u250c\u2510\u2514\u2518\u253c\u2534\u252c\u2524\u251c' +
        u'\u2591\u2592\u2261\xb1\u2320\u2248\xb7\u25a0' +

        # Rogue level IBMgraphics...
        u'\u2551\u2550\u2554\u2557\u255a\u255d\u256c\u2569\u2566\u2563\u2560' +
        u'\u263a\u2666\u2663\u2640\u266b\u263c\u2191[\xa1\u2592\u2593\u03c4' + 
        u'\u2261\xb7'
    ),
    # And... the normal way we expect them...
    u"|--------||####{}.||-----+--||@^:,?*)]!##/%.")
)

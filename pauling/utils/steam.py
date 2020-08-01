class SteamID():
    
    def __init__(self):
        self.steamid64ident = 76561197960265728

    def usteamid_to_commid(self, usteamid: str) -> int:
        for ch in ['[', ']']:
            if ch in usteamid:
                usteamid = usteamid.replace(ch, '')

        usteamid_split = usteamid.split(':')
        commid = int(usteamid_split[2]) + self.steamid64ident

        return commid

if __name__ == '__main__':
    steam = SteamID()
    print(steam.usteamid_to_commid("[U:1:69316398]"))
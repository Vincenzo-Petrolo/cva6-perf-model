class ReservationStationPickPolicy(object):
    """Reservation Station Pick Policy."""

    def pickFirstReady(rs):
        """Pick the next entry ready for execution from the RS.
        Iterate in increasing order of the index, and return the first entry
        that is ready for execution.
        """
        for e in rs.entries:
            if e["status"] == "ready":
                e["status"] = "executing"
                return e
        return None
    
    def pickRandom(rs):
        """Pick the next entry ready for execution from the RS.
        Pick a random entry that is ready for execution.
        """
        import random
        entries_copy = rs.entries.copy()

        random.shuffle(entries_copy)
        for e in entries_copy:
            if e["status"] == "ready":
                e["status"] = "executing"
                return e
        return None
    
    def pickLastReady(rs):
        """Pick the next entry ready for execution from the RS.
        Pick the oldest entry that is ready for execution.
        """
        entries_copy = rs.entries.copy()

        entries_copy.reverse()

        for e in entries_copy:
            if e["status"] == "ready":
                e["status"] = "executing"
                return e
        return None
    
    def pickOldestReady(rs):
        """Pick the next entry ready for execution from the RS.
        Pick the oldest entry that is ready for execution.
        """
        i = rs.oldest_ptr
        cnt = 0

        while cnt < rs.n_entries:

            if rs.entries[i]["status"] == "ready":
                rs.entries[i]["status"] = "executing"
                return rs.entries[i]

            i = (i + 1) % rs.n_entries
            cnt += 1
        
        return None

    def pickNewestReady(rs):
        """Pick the next entry ready for execution from the RS.
        Pick the oldest entry that is ready for execution.
        """
        i = rs.newest_ptr
        cnt = 0

        while cnt < rs.n_entries:
            if rs.entries[i]["status"] == "ready":
                rs.entries[i]["status"] = "executing"
                return rs.entries[i]

            i = (i - 1) % rs.n_entries
            cnt += 1

        
        return None
    
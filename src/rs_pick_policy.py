class ReservationStationPickPolicy(object):
    """Reservation Station Pick Policy."""

    def pickFirstReady(rs, status : str, next_status : str):
        """Pick the next entry ready for execution from the RS.
        Iterate in increasing order of the index, and return the first entry
        that is ready for execution.
        """
        for e in rs.entries:
            if e["status"] == status:
                e["status"] = next_status
                return e
        return None
    
    def pickRandom(rs, status : str, next_status : str):
        """Pick the next entry ready for execution from the RS.
        Pick a random entry that is ready for execution.
        """
        import random
        entries_copy = rs.entries.copy()

        random.shuffle(entries_copy)
        for e in entries_copy:
            if e["status"] == status:
                e["status"] = next_status
                return e
        return None
    
    def pickLastReady(rs, status : str, next_status : str):
        """Pick the next entry ready for execution from the RS.
        Pick the oldest entry that is ready for execution.
        """
        entries_copy = rs.entries.copy()

        entries_copy.reverse()

        for e in entries_copy:
            if e["status"] == status:
                e["status"] = next_status 
                return e
        return None
    
    def pickOldestReady(rs, status : str, next_status : str):
        """Pick the next entry ready for execution from the RS.
        Pick the oldest entry that is ready for execution.
        """
        i = rs.oldest_ptr
        cnt = 0

        while cnt < rs.n_entries:

            if rs.entries[i]["status"] == status:
                rs.entries[i]["status"] = next_status 
                return rs.entries[i]

            i = (i + 1) % rs.n_entries
            cnt += 1
        
        return None

    def pickNewestReady(rs, status : str, next_status : str):
        """Pick the next entry ready for execution from the RS.
        Pick the oldest entry that is ready for execution.
        """
        i = rs.newest_ptr
        cnt = 0

        while cnt < rs.n_entries:
            if rs.entries[i]["status"] == status:
                rs.entries[i]["status"] = next_status 
                return rs.entries[i]

            i = (i - 1) % rs.n_entries
            cnt += 1

        
        return None
    
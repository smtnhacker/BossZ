try:
    from replit import db
except Exception:
    try:
        from mock_db import db
    except Exception:
        # for unit testing
        import sys
        sys.path.append('./')
        from mock_db import DBClass
        db = DBClass()

def _get_free_uid():
    uid = db.get('uid', '0')
    return uid

def insert_unique(data):
    uid = int(_get_free_uid())
    db[str(uid)] = data
    db['uid'] = str(uid + 1)
    print(f'Entry #{uid} created successfully.')
    return uid

def insert_reminder(date, uid):
    date_list = db.get(date, list())
    date_list.append(uid)
    db[date] = date_list
    return True

def get_reminders(date):
    date_list = db.get(date, list())
    return date_list

def get_reminder(uid):
    return db.get(str(uid), None)

def finished_reminder(uid):
    print(f'Trying to finish reminder #{uid}.')
    uid = str(uid)
    if uid in db.keys():
        temp_db = db[uid]
        temp_db['done'] = True
        db[uid] = temp_db
        print(f'Entry #{uid} finished successfully.')
        return True
    else:
        return False

def _main():
    db.reload()
    print(f'Testing insert_unique')
    original_uid = _get_free_uid()
    RANDOM_DATA = [
        'A string',
        1234,
        ('A', 'tuple'),
        ['A', 'list'],
        ['A', ['nested', ['list']]],
    ]
    try:
        for data in RANDOM_DATA:
            insert_unique(data)
            print(f'Successfully inserted inserted unique {type(data)}')
    except Exception as e:
        exception = f"{type(e).__name__}: {e}"
        print(exception)
    finally:
        ok = True
        for uid in range(int(original_uid), int(_get_free_uid())):
            ok &= db.delete(str(uid))
        db['uid'] = original_uid
        if ok: print('Successfully reverted insert_unique tests')
        else: print('Revertion failed')
    
    print('---------------')
    print(f'Testing insert_reminder')

    import datetime
    sample = {
            'label' : 'Sample Label',
            'author' : 'Sample name',
            'user_id' : 'Sample user_id',
            'done' : False,
            'guild' : 'Sample guild',
            'channel' : 'Sample channel',
        }
    db["-1"] = sample
    now = datetime.datetime.now()
    if insert_reminder(str(now), -1):
        print('Successfully inserted sample')
    else: print('Failed to insert sample')
    
    print("keys: ", db.keys())

    print('Testing finished_reminder')
    if finished_reminder(-1):
        print(f'Successfully finished sample reminder')
    else: print('Failed to finish sample reminder')

    if db.delete("-1"): print(f'Successfully deleted sample reminder')
    else: print('Failed to delete sample reminder')

if __name__ == '__main__':
    _main()
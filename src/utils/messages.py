def log(msg, pbar):
    if pbar:
        pbar.write(msg)
    else:
        print(msg)


def dry_run_log(msg, pbar):
    if pbar:
        pbar.write_dry_run_log(msg)
    else:
        print(msg)


def update_pbar(n, pbar):
    if pbar:
        pbar.update(n)
    else:
        print(f"Progress: {n}")

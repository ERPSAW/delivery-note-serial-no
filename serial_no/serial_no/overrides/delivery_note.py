import frappe
import re
from collections import defaultdict

@frappe.whitelist()
def format_serial_ranges(bundle):
    if not bundle:
        return ""
    serials = []
    result = frappe.db.sql("""SELECT serial_no from `tabSerial and Batch Entry` WHERE parent = %(bundle)s""",{"bundle":bundle},as_dict=1)
    for row in result:
        serials.append(row.serial_no)
    if not serials:
        return ""
    def split_serial(s):
        match = re.match(r"^(.*?)(\d+)$", s)
        if not match:
            return None
        return match.group(1), match.group(2)

    prefix_map = defaultdict(list)
    invalid_serials = []

    # Group valid serials and collect invalid ones
    for serial in serials:
        result = split_serial(serial)
        if result:
            prefix, number = result
            prefix_map[prefix].append(number)
        else:
            invalid_serials.append(serial)

    condensed_ranges = []

    for prefix, numbers in prefix_map.items():
        # Sort numerically
        numbers = sorted(numbers, key=lambda x: int(x))
        padding = len(numbers[0])

        group = []
        for num_str in numbers:
            num = int(num_str)
            if not group:
                group = [num]
            elif num == group[-1] + 1:
                group.append(num)
            else:
                # Output previous group
                if len(group) == 1:
                    condensed_ranges.append(f"{prefix}{group[0]:0{padding}}")
                else:
                    condensed_ranges.append(f"{prefix}{group[0]:0{padding}}...{group[-1]:0{padding}}")
                group = [num]

        # Output last group
        if group:
            if len(group) == 1:
                condensed_ranges.append(f"{prefix}{group[0]:0{padding}}")
            else:
                condensed_ranges.append(f"{prefix}{group[0]:0{padding}}...{group[-1]:0{padding}}")

    # Add invalid serials at the end
    condensed_ranges.extend(invalid_serials)

    return "<br>".join(condensed_ranges)
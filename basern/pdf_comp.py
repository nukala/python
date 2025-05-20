from typing import Set, List, Tuple
import sys
import traceback


class PageNumberParser:
    verbose = 0

    def __init__(self):
        pass

    @staticmethod
    def parse_range_element(element: str, verbose: int = 0) -> Set[int]:
        """Parse a single element of a range expression (e.g., '1', '3-10')."""
        try:
            if '-' in element:
                # Handle range like '3-10'
                start_str, end_str = element.split('-', 1)
                start, end = int(start_str), int(end_str)
                return set(range(start, end + 1))  # Include both ends
            else:
                # Handle single number
                return {int(element)}
        except ValueError:
            if verbose > 0:
                traceback.print_exc() 

            return set()

    def get_content_to_parse(self, input_str: str) -> str:
        # # Remove any prefix (e.g., '-p')
        # match = re.match(r'(?:-\w+)?(.+)', input_str)
        # if not match:
        #     return set()
        #
        # content = match.group(1)
        orig = input_str
        content = input_str
        if '-p' in input_str:
            content = input_str.split('-p')[-1]
        if '.' in content:
            content = content.split('.')[-2]
        if self.verbose > 0:
            print(f"Original string={orig}, to_parse={content}\n")

        return content

    def parse_range_string(self, input_str: str) -> Set[int]:
        """
        Parse a string like '-p1,3-10,12,14-18' into a set of integers.
        
        Args:
            input_str: String containing comma-separated list of numbers and ranges
            
        Returns:
            Set of integers represented by the input string
        """
        result: Set[int] = set()
        # if '-p' not in input_str:
        #     if self.verbose >= 1:
        #         print("Is there a page number in [{input_str}]")
        #     return result

        content = self.get_content_to_parse(input_str)
        if self.verbose > 1:
            print(f"From input=[{input_str}], parsing=[{content}]")
        # Split by comma and parse each element
        for element in content.split(','):
            if element:  # Skip empty elements
                result.update(self.parse_range_element(element, self.verbose))
                
        return result

    @staticmethod
    def format_range_set(numbers: Set[int]) -> str:
        """
        Format a set of integers into a human-readable string with ranges.
        
        Example: {1, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 15, 16, 17, 18}
        Becomes: "1, 3 to 10, 12, 14 to 18"
        """
        if not numbers:
            return ""
        
        # Sort the numbers
        sorted_nums = sorted(numbers)
        
        # Group consecutive numbers
        ranges: List[Tuple[int, int]] = []
        start = end = sorted_nums[0]
        
        for num in sorted_nums[1:]:
            if num == end + 1:
                # Extend current range
                end = num
            else:
                # End current range and start a new one
                ranges.append((start, end))
                start = end = num
        
        # Add the last range
        ranges.append((start, end))
        
        # Format each range
        result = []
        for start, end in ranges:
            if start == end:
                result.append(str(start))
            else:
                result.append(f"{start} to {end}")
        
        return ", ".join(result)


if __name__ == "__main__":
    fn = sys.argv[1]
    p = PageNumberParser()
    p.verbose = 4
    print(f"parsing [{fn}]")
    nums = p.parse_range_string(fn)
    print(f"  set=[{nums}]\n  reader-friendly = [{p.format_range_set(nums)}]\n")


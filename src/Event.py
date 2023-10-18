class Event:

    def __init__(self, name, start_date, end_date, priority, event_type, event_url="",location="None", description=""):
        """
        Function:
            __init__
        Description:
            Creates a new Event object instance
        Input:
            self - The current Event object instance
            name - String name of the event
            start_date - datetime object representing the start of an event
            end_date - datetime object representing the end of an event
            priority - priority value of an event
            event_type - String representing the type of event
            description - Optional text field that contains any additional notes about an event (can be blank)
        Output:
            - A new Event object instance
        """
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.priority = priority
        self.event_type = event_type
        self.url = event_url
        self.location=location
        self.description = description

    def __str__(self):
        """
        Function:
            __str__
        Description:
            Converts an Event object into a string
        Input:
            self - The current Event object instance
        Output:
            A formatted string that represents all the information about an Event instance
        """
        output = (
            self.name
            + " "
            + str(self.start_date)
            + " "
            + str(self.end_date)
            + " "
            + str(self.priority)
            + " "
            + self.event_type
            + " "
            + self.url
            + " "
            + self.location
            + " "
            + self.description
        )
        return output

    def __lt__(self, other):
        """
        Function:
            __lt__
        Description:
            Finds whether the current event starts before another
        Input:
            self - The current Event object instance
            other - The Event object we are comparing self to
        Output:
            True - self starts before other
            False - self starts after other
        """
        return self.start_date < other.start_date

    def __le__(self, other):
        """
        Function:
            __le__
        Description:
            Finds whether the current event starts before or at the same time as another
        Input:
            self - The current Event object instance
            other - The Event object we are comparing self to
        Output:
            True - self starts before or at the same time as other
            False - self comes after other
        """
        return self.start_date <= other.start_date

    def __gt__(self, other):
        """
        Function:
            __gt__
        Description:
            Finds whether the current event starts after another
        Input:
            self - The current Event object instance
            other - The Event object we are comparing self to
        Output:
            True - self starts after other
            False - self comes before other
        """
        return self.start_date > other.start_date

    def __ge__(self, other):
        """
        Function:
            __ge__
        Description:
            Finds whether the current event starts after or at the same time as another
        Input:
            self - The current Event object instance
            other - The Event object we are comparing self to
        Output:
            True - self starts after or at the same time as other
            False - self comes before other
        """
        return self.start_date >= other.start_date

    def intersect(self, other):
        """
        Function:
            intersect
        Description:
            Finds whether the current event intersects another in one of 4 possible ways:
            # Case 1: The start and end dates for the event occur inside another event
            # Case 2: The start and end dates for the event encompass another event
            # Case 3: Only the start date for the event occurs inside another event
            # Case 4: Only the end date for the event occurs inside another event
        Input:
            self - The current Event object instance
            other - The Event object we are comparing self to
        Output:
            True - self intersects with other
            False - self does not intersect with other
        """
        return (self.start_date <= other.start_date <= self.end_date) or (
            other.start_date <= self.start_date <= other.end_date
        )

    def to_list(self):
        """
        Function:
            to_list
        Description:
            Converts an Event object into a list
        Input:
            self - The current Event object instance
        Output:
            array - A list with each index being an attribute of the self Event object
        """
        array = [self.name, str(self.start_date), str(self.end_date), str(self.priority), self.event_type, self.url, self.location, self.description]
        return array
class ReportTimeSpanDefn:
    # definition of the output report to create
    def __init__(self, output_folder, from_date, to_date):
        self.output_folder = output_folder
        self.from_date = from_date
        self.to_date = to_date
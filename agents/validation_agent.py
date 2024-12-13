class ValidationAgent:
    def __init__(self, vision, mission):
        self.vision = vision
        self.mission = mission

    def run(self, aggregated_content):
        content = aggregated_content["content"]
        if self.vision in content and self.mission in content:
            status = "good"
        else:
            status = "bad"
        return {"content": content, "status": status}

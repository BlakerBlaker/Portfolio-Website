import yaml
from bs4 import BeautifulSoup

# Load the main YAML file
with open("Builder.yaml", "r", encoding="utf-8") as builder_file:
    builder_content = yaml.safe_load(builder_file)

# Load the image list YAML file
with open("ImageList.yaml", "r", encoding="utf-8") as image_list_file:
    image_list_content = yaml.safe_load(image_list_file)

# Merge the image list into the main content
builder_content["master_images"] = image_list_content["master_images"]

# Create a dictionary for quick lookup of images by ID
image_lookup = {img["id"]: img for img in builder_content["master_images"]}

# Load the HTML file with the correct encoding
html_file = "template.html"
with open(html_file, "r", encoding="utf-8") as file:
    soup = BeautifulSoup(file, "html.parser")

# Helper function to resolve image references
def resolve_image(image_id):
    return image_lookup.get(image_id, {})

# Helper function to check if an image is used in the projects section
def get_project_link(image_id):
    for project in builder_content["sections"][1]["projects"]:
        if project["image"] == image_id:
            return project["link"]
    return None

# Update the home section
home_section = soup.find("section", {"id": "home"})
if home_section:
    background_image = resolve_image(builder_content["sections"][0]["background_image"])
    if background_image:
        home_section["style"] = f"background-image: url('{background_image['src']}');"

# Update the projects section
projects_section = soup.find("section", {"id": "projects"})
if projects_section:
    container = projects_section.find("div", {"class": "container"})
    if container:
        container.clear()  # Clear existing content
        # Add a title for the Projects section
        title = soup.new_tag("h3", **{"class": "text-3xl font-bold mb-8 text-center"})
        title.string = builder_content["sections"][1]["title"]
        container.append(title)

        # Create a grid for project cards
        grid = soup.new_tag("div", **{"class": "grid md:grid-cols-2 lg:grid-cols-3 gap-6"})
        container.append(grid)

        # Iterate over projects and populate the grid
        for project in builder_content["sections"][1]["projects"]:
            project_image = resolve_image(project["image"])
            if project_image:
                # Create a project card
                card = soup.new_tag("div", **{"class": "bg-gray-50 p-4 rounded shadow"})
                grid.append(card)

                # Add the project image
                img = soup.new_tag("img", src=project_image["src"], alt=project_image["alt"], **{"class": "mb-4 rounded"})
                card.append(img)

                # Add the project title as a link
                title = soup.new_tag("h4", **{"class": "font-bold text-lg"})
                link = soup.new_tag("a", href=project["link"], **{"class": "hover:underline"})
                link.string = project["title"]
                title.append(link)
                card.append(title)

# Update the gallery section
gallery_section = soup.find("section", {"id": "gallery"})
if gallery_section:
    gallery_grid = gallery_section.find("div", {"class": "grid"})
    if gallery_grid:
        gallery_grid.clear()  # Clear existing gallery items
        for image in builder_content["master_images"]:
            if image["enabled"]:  # Only include enabled images
                # Create a container for the image and caption
                container = soup.new_tag("div", **{"class": "text-center"})
                
                # Add the image
                img_tag = soup.new_tag("img", src=image["src"], alt=image["alt"], **{"class": "rounded shadow mb-2"})
                container.append(img_tag)
                
                # Check if the image is used in the projects section
                project_link = get_project_link(image["id"])
                if project_link:
                    # Wrap the caption in a link
                    caption_tag = soup.new_tag("a", href=project_link, **{"class": "text-sm text-blue-600 underline"})
                    caption_tag.string = image["caption"]
                else:
                    # Add the caption as plain text
                    caption_tag = soup.new_tag("p", **{"class": "text-sm text-gray-600"})
                    caption_tag.string = image["caption"]
                
                container.append(caption_tag)
                gallery_grid.append(container)

# Save the updated HTML file
updated_html_file = "portfolio.html"
with open(updated_html_file, "w", encoding="utf-8") as file:
    file.write(str(soup))

print(f"HTML file updated and saved as {updated_html_file}")
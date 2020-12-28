# DashboardLeaf

Flask server for displaying multiple dashboards with custom tiles that refresh periodically.

## Page

Holds multiple tiles and displays them in a grid. On mobile devices in portrait orientation the grid will be displayed as a single column.

## Tile

A tile is displayed on a page and shows arbitrary information. It is possible to create custom tiles.

### Tile properties
- `x` - horizontal position in the grid, starting by 0 (**Note:** Positions should not be assigned more than once!)
- `y` - vertical position in the grid, starting by 0 (**Note:** Positions should not be assigned more than once!)
- `width` - ???


### Create a custom tile

1. Create a new tile inside `folder_name` using the following template:

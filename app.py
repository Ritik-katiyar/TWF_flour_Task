from flask import Flask, request, jsonify
from itertools import permutations
from math import ceil

app = Flask(__name__)

distanceMap = {
    'C1': {'C2': 4, 'C3': 3, 'L1': 3},
    'C2': {'C1': 4, 'C3': 2, 'L1': 2.5},
    'C3': {'C1': 3, 'C2': 2, 'L1': 2},
    'L1': {'C1': 3, 'C2': 2.5, 'C3': 2}
}

stockProduct = {
    'A': ('C1', 3),
    'B': ('C1', 2),
    'C': ('C1', 8),
    'D': ('C2', 12),
    'E': ('C2', 25),
    'F': ('C2', 15),
    'G': ('C3', 0.5),
    'H': ('C3', 1),
    'I': ('C3', 2)
}

def get_cost(weight, distance):
    if weight <= 5:
        return 10 * distance
    extra = ceil((weight - 5) / 5)
    return distance * (10 + extra * 8)

def OrderToCenters(order):
    centers = {}
    for product, quantity in order.items():
        if quantity == 0:
            continue
        center, unit_weight = stockProduct[product]
        centers[center] = centers.get(center, 0) + quantity * unit_weight
    return centers

def generatePath(start, centers):
    points = list(centers)
    if start not in points:
        return []
    paths = []
    for perm in permutations(points):
        if perm[0] != start:
            continue
        path = []
        for loc in perm:
            path.append(loc)
            path.append('L1')
        paths.append(path)
    return paths

def calculateRouteCost(path, pickups):
    load = 0
    cost = 0
    pickups = pickups.copy()
    for i in range(len(path) - 1):
        frm, to = path[i], path[i+1]
        if frm in pickups:
            load += pickups[frm]
            pickups.pop(frm)
        dist = distanceMap[frm][to]
        cost += get_cost(load, dist)
        if to == 'L1':
            load = 0
    return cost

def calculateMinCost(order):
    centers = OrderToCenters(order)
    if not centers:
        return 0

    min_cost = float('inf')
    for start in centers.keys():
        paths = generatePath(start, centers)
        for path in paths:
            cost = calculateRouteCost(path, centers)
            min_cost = min(min_cost, cost)
    return round(min_cost, 2)

@app.route('/calculate_cost', methods=['POST'])
def calculate_cost():
    try:
        order = request.json
        if not isinstance(order, dict):
            return jsonify({"error": "Invalid order format"}), 400

        cost = calculateMinCost(order)
        return jsonify({"cost": cost}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

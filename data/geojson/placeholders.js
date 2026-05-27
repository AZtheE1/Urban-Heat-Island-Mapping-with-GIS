// GIS and Coordinate Presets for Urban Heat Island mapping
// Used by Pair A (GIS) and Pair C (Frontend) to render maps and center views dynamically.

const REGION_PRESETS = {
  mirpur12: {
    name: "Mirpur 12 (Baseline Micro-analysis)",
    center: [23.8243, 90.3653],
    zoom: 15,
    bounds: [[23.8200, 90.3600], [23.8300, 90.3700]],
    geojson: {
      type: "FeatureCollection",
      features: [
        {
          type: "Feature",
          properties: { name: "Mirpur 12 High-Heat Zone", intensity: 0.9, avg_lst: 37.5 },
          geometry: {
            type: "Polygon",
            coordinates: [
              [
                [90.3600, 23.8200],
                [90.3700, 23.8200],
                [90.3700, 23.8260],
                [90.3600, 23.8260],
                [90.3600, 23.8200]
              ]
            ]
          }
        },
        {
          type: "Feature",
          properties: { name: "Mirpur DOHS Cool Canopy Zone", intensity: 0.3, avg_lst: 29.5 },
          geometry: {
            type: "Polygon",
            coordinates: [
              [
                [90.3600, 23.8260],
                [90.3700, 23.8260],
                [90.3700, 23.8300],
                [90.3600, 23.8300],
                [90.3600, 23.8260]
              ]
            ]
          }
        }
      ]
    }
  },
  dhaka_all: {
    name: "Entire Dhaka Metropolitan Area",
    center: [23.8103, 90.4125],
    zoom: 11,
    bounds: [[23.6500, 90.3000], [23.9500, 90.5000]],
    geojson: {
      type: "FeatureCollection",
      features: [
        {
          type: "Feature",
          properties: { name: "Dhaka Core Urban Heat Island", intensity: 0.85, avg_lst: 36.2 },
          geometry: {
            type: "Polygon",
            coordinates: [
              [
                [90.3500, 23.7500],
                [90.4500, 23.7500],
                [90.4500, 23.8500],
                [90.3500, 23.8500],
                [90.3500, 23.7500]
              ]
            ]
          }
        }
      ]
    }
  },
  sylhet: {
    name: "Sylhet Division",
    center: [24.8949, 91.8687],
    zoom: 12,
    bounds: [[24.8500, 91.8000], [24.9500, 91.9500]],
    geojson: {
      type: "FeatureCollection",
      features: [
        {
          type: "Feature",
          properties: { name: "Sylhet Urban Core", intensity: 0.5, avg_lst: 32.1 },
          geometry: {
            type: "Polygon",
            coordinates: [
              [
                [91.8500, 24.8800],
                [91.9000, 24.8800],
                [91.9000, 24.9200],
                [91.8500, 24.9200],
                [91.8500, 24.8800]
              ]
            ]
          }
        }
      ]
    }
  },
  rajshahi: {
    name: "Rajshahi Division",
    center: [24.3745, 88.6042],
    zoom: 12,
    bounds: [[24.3300, 88.5500], [24.4200, 88.6500]],
    geojson: {
      type: "FeatureCollection",
      features: [
        {
          type: "Feature",
          properties: { name: "Rajshahi Urban Hotspots", intensity: 0.8, avg_lst: 38.4 },
          geometry: {
            type: "Polygon",
            coordinates: [
              [
                [88.5700, 24.3500],
                [88.6300, 24.3500],
                [88.6300, 24.4000],
                [88.5700, 24.4000],
                [88.5700, 24.3500]
              ]
            ]
          }
        }
      ]
    }
  },
  chittagong: {
    name: "Chittagong Division",
    center: [22.3569, 91.7832],
    zoom: 12,
    bounds: [[22.3000, 91.7000], [22.4200, 91.8500]],
    geojson: {
      type: "FeatureCollection",
      features: [
        {
          type: "Feature",
          properties: { name: "Chittagong Industrial & Port Heat Belt", intensity: 0.75, avg_lst: 34.8 },
          geometry: {
            type: "Polygon",
            coordinates: [
              [
                [91.7300, 22.3200],
                [91.8100, 22.3200],
                [91.8100, 22.3800],
                [91.7300, 22.3800],
                [91.7300, 22.3200]
              ]
            ]
          }
        }
      ]
    }
  }
};

// Export for Node/CommonJS environment if backend loads it, or expose globally for frontend.
if (typeof module !== 'undefined' && module.exports) {
  module.exports = REGION_PRESETS;
}

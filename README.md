# ETS2 Local Radio - Linux Fork

A refactored and modularized version of the ETS2 Local Radio application with real-time coordinate tracking for Linux systems.

## Features

- **Real-time Position Tracking**: Uses ETS2 telemetry plugin for live coordinate monitoring
- **Location-based Radio**: Automatic station switching based on your truck's location
- **Signal Strength Simulation**: Realistic signal strength calculation based on distance from cities
- **Multi-country Support**: Supports radio stations from multiple European countries
- **Web Interface**: Modern, responsive web interface with real-time updates
- **Modular Architecture**: Clean, maintainable code structure

## Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd ets2-local-radio
```

2. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

3. **Install ETS2 Telemetry Plugin** (optional but recommended):
   - Download and install the ETS2 telemetry plugin for real-time tracking
   - Without this plugin, the application will work in manual mode

4. **Place data files** (optional):
   - `cities.json`: Official city database for accurate city positions
   - `stations.json`: Custom radio station database

## Usage

### Running the Application

```bash
python main.py
```

The application will start and be available at `http://localhost:5000`

### Configuration

You can configure the application by modifying `config.py` or using environment variables:

- `ETS2_HOST`: Server host (default: 0.0.0.0)
- `ETS2_PORT`: Server port (default: 5000)
- `ETS2_DEBUG`: Enable debug mode (default: false)

### Using the Web Interface

1. Open `http://localhost:5000` in your browser
2. If telemetry is connected, drive around in ETS2 to experience automatic station switching
3. Manual station selection is always available regardless of telemetry status

## Project Structure

```
ets2_radio/
├── main.py                 # Application entry point
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── README.md             # This documentation
├── core/
│   ├── __init__.py
│   ├── radio_controller.py    # Main application logic
│   └── background_monitor.py  # Background coordinate monitoring
├── data/
│   ├── __init__.py
│   ├── city_database.py      # City database management
│   └── station_manager.py    # Radio station management
├── telemetry/
│   ├── __init__.py
│   └── coordinate_reader.py  # ETS2 telemetry integration
├── web/
│   ├── __init__.py
│   ├── app.py              # Flask application setup
│   ├── routes.py           # API route definitions
│   └── templates.py        # HTML templates
├── utils/
│   ├── __init__.py
│   ├── file_helpers.py     # File utilities
│   └── math_helpers.py     # Mathematical utilities
└── tests/                  # Unit tests (future)
```

## Architecture

### Core Components

- **RadioController**: Main application logic and state management
- **BackgroundMonitor**: Background thread for coordinate monitoring
- **ETS2CoordinateReader**: Telemetry plugin integration
- **ETS2CityDatabase**: City data loading and querying
- **StationManager**: Radio station management and parsing

### Benefits of Modular Design

1. **Maintainability**: Each component has a single responsibility
2. **Testability**: Individual components can be unit tested
3. **Extensibility**: Easy to add new features without affecting existing code
4. **Collaboration**: Multiple developers can work on different components
5. **Debugging**: Issues are localized to specific components

## API Endpoints

- `GET /`: Web interface
- `GET /api/status`: Complete application status
- `GET /api/stations/<country>`: Stations for a specific country
- `GET /api/cities/<country>`: Cities for a specific country
- `GET /api/random_station`: Random station for current country
- `POST /api/reload_stations`: Reload stations from remote source
- `GET /api/coordinates`: Current coordinates

## Development

### Adding New Features

1. **New telemetry sources**: Extend `telemetry/coordinate_reader.py`
2. **New data sources**: Add modules to `data/` package
3. **New web features**: Add routes to `web/routes.py`
4. **New utilities**: Add functions to `utils/` package

### Testing

```bash
# Run unit tests (when implemented)
python -m pytest tests/

# Test individual components
python -c "from data.city_database import ETS2CityDatabase; db = ETS2CityDatabase(); print(f'Loaded {db.get_city_count()} cities')"
```

### Configuration

All configuration is centralized in `config.py`. Key settings include:

- File paths for data files
- Telemetry settings
- Signal strength calculations
- Web server configuration
- Country mappings

## Troubleshooting

### Common Issues

1. **"ETS2 telemetry plugin not found"**
   - Install the ETS2 telemetry plugin
   - Ensure ETS2 is running with the plugin active
   - Check that `/dev/shm/SCS/SCSTelemetry` exists

2. **"No stations available"**
   - Check internet connection for remote station loading
   - Verify `stations.json` file format if using local stations
   - Try reloading stations via the web interface

3. **"Connection error"**
   - Ensure the application is running
   - Check that port 5000 is not blocked
   - Verify Flask is properly installed

### Debug Mode

Enable debug mode for detailed logging:

```bash
export ETS2_DEBUG=true
python main.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes following the modular architecture
4. Add tests for new functionality
5. Submit a pull request

## License

This project is based on the original ETS2 Local Radio project and enhanced for Linux systems with a modular architecture.

## Credits

- Original ETS2 Local Radio: https://github.com/Koenvh1/ets2-local-radio/
- Station data: https://localradio.koenvh.nl/
- ETS2 Telemetry Plugin: Various contributors to the ETS2 modding community

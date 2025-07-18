# ETS2 Local Radio - Linux Fork

A Python based version of the ETS2 Local Radio application with real-time coordinate tracking for Linux systems.
Still in development. This application does NOT have feature parity with https://github.com/Koenvh1/ets2-local-radio.
Requires the native Linux version of ETS2. It will not work with Proton.

## Features

- **Real-time Position Tracking**: Uses jackz314 ETS2 SDK plugin fork for Linux for live coordinate monitoring
- **Multi-country Support**: Supports radio stations from multiple European countries
- **Web Interface**: Modern, responsive web interface with real-time updates

## Todo

- **Location-based Radio**: Automatic station switching based on your truck's location
- **Signal Strength Simulation**: Realistic signal strength calculation based on distance from cities
- **Controller input**: Switch channels using a controller (on my wishlist but not sure this is feasible with Python/Flask)
- **Static interference**: Interference like Koenvh1's version when signal strength is low.

## Installation

1. **Clone the repository**:
```bash
git clone https://github.com/macaon/ets2-local-radio-linux
cd ets2-local-radio
```

2. **Create and activate venv**:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

4. **Compile and install ETS2 SDK plugin**:
```bash
# Clone and build the plugin
git clone https://github.com/jackz314/scs-sdk-plugin.git
cd scs-sdk-plugin

# Build
mkdir build && cd build
cmake .. && make

# Install to ETS2
cp *.so ~/.local/share/Steam/steamapps/common/Euro\ Truck\ Simulator\ 2/bin/linux_x64/plugins/
```

5. **Download cities data**:
   - Download cities.json from https://github.com/Koenvh1/ETS2-City-Coordinate-Retriever and place it into the base script directory.
   (It's possible that this file is grossly outdated, but for now this is what the script is working with).

## Usage

### Running the Application

```bash
source venv/bin/activate
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
2. If telemetry is connected, drive around in ETS2.
3. Manual station selection is always available regardless of telemetry status

## Architecture

### Core Components

- **RadioController**: Main application logic and state management
- **BackgroundMonitor**: Background thread for coordinate monitoring
- **ETS2CoordinateReader**: Telemetry plugin integration
- **ETS2CityDatabase**: City data loading and querying
- **StationManager**: Radio station management and parsing

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

## Troubleshooting

### Common Issues

1. **"ETS2 telemetry plugin not found"**
   - Install the ETS2 telemetry plugin
   - Ensure ETS2 is running with the plugin active (you should be notified about SDK features when launching the game)
   - Check that `/dev/shm/SCS/SCSTelemetry` exists

2. **"No stations available"**
   - Check internet connection for remote station loading (shamelessly uses https://localradio.koenvh.nl/stations/stations-europe.js)
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

This project is based on the original ETS2 Local Radio project and is being ported to Linux.

## Credits

- Original ETS2 Local Radio: https://github.com/Koenvh1/ets2-local-radio/
- Station data: https://localradio.koenvh.nl/
- ETS2 Telemetry Plugin: Various contributors to the ETS2 modding community (https://github.com/jackz314, https://github.com/RenCloud, https://github.com/nlhans)

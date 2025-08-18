# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MLLM AiCar 클라이언트 - A client application for using MLLM AI in vehicles. Originally inspired by OpenAI's realtime API console but heavily modified to work with a custom server backend instead of OpenAI's servers.

## Development Commands

### Start Development Server
```bash
npm start
```

### Build for Production
```bash
npm run build
```

### Run Tests
```bash
npm run test
```

### Start Relay Server
```bash
npm run relay
```

## Architecture Overview

### Frontend Structure
- **React + TypeScript** application with routing via `react-router`
- **Three main pages**:
  - `/` - AdvancedChat (primary interface with LangChain integration)
  - `/chatbot` - Basic chat interface
  - `/console` - OpenAI realtime console interface

### Key Components
- `AdvancedChat` (`src/pages/AdvancedChat/Console.tsx`) - Main chat interface with LangGraph integration
- `ChatContent` (`src/components/chatbot/ChatContent.tsx`) - Chat message handling and display
- `LangGraph` (`src/components/chatbot/LangGraph.tsx`) - State graph visualization and event handling
- `SpeechToText` - Speech recognition capabilities

### Communication Architecture
- **Primary Backend**: Custom server at `http://127.0.0.1:8000/agent` (LangChain-based)
- **Relay Server**: Node.js WebSocket relay (`relay-server/`) for OpenAI API integration
- **Session Management**: UUID-based sessions with server-side persistence

### Audio Processing
- Custom `wavtools` library for audio recording, streaming, and playback
- WebRTC audio processing with worklets
- Real-time audio analysis capabilities

## Key Technologies
- React 18 with TypeScript
- SASS for styling
- WebSocket connections for real-time communication
- LangChain integration for advanced AI workflows
- Leaflet for mapping functionality
- Audio Web APIs for speech processing

## Environment Configuration
- Requires `.env` file with `OPENAI_API_KEY` for relay server
- Default relay server port: 8081
- Main backend expects to run on port 8000

## Server Dependencies
The client expects a companion server running on port 8000 with endpoints:
- `/agent` - Main chat/agent endpoint
- `/agent/sessions` - Session management
- LangGraph state visualization endpoints
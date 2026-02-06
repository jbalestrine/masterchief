# Restart the inspircd service via compose
docker compose -f tools/irc_stack_compose.yml restart inspircd

# Show latest logs to confirm InspIRCd started without loading the disabled modules
docker logs inspircd --tail 200
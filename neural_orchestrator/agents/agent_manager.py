"""
Agent Management System with Git Listing
Manages agents with git-based configuration and anti-imposter verification.
"""

import asyncio
import subprocess
import json
import hashlib
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
import uuid


class AgentStatus(Enum):
    """Status of agents."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    BLOCKED = "blocked"
    VERIFIED = "verified"
    UNVERIFIED = "unverified"


class AgentType(Enum):
    """Types of agents."""
    MONITORING = "monitoring"
    STEERING = "steering"
    VERIFICATION = "verification"
    ROUTING = "routing"
    ANALYSIS = "analysis"


@dataclass
class AgentConfig:
    """Configuration for an agent."""
    agent_id: str
    name: str
    agent_type: AgentType
    git_repo: str
    git_branch: str
    config_path: str
    status: AgentStatus
    created_at: str
    last_updated: str
    permissions: List[str]
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class AgentAction:
    """Represents an agent action."""
    action_id: str
    agent_id: str
    action_type: str
    target: str
    parameters: Dict[str, Any]
    timestamp: str
    status: str
    result: Optional[Dict[str, Any]] = None


@dataclass
class GitAgentListing:
    """Git-based agent listing for verification."""
    repo_url: str
    branch: str
    commit_hash: str
    agents: List[str]
    verified: bool
    last_sync: str


class AgentManager:
    """
    Manages agents with git-based configuration and listing.
    Roots out false flags, imposters, and only routes to real linked successive confirmed agents.
    """

    def __init__(self, workspace_dir: str = "agent_workspace"):
        self.workspace_dir = Path(workspace_dir)
        self.workspace_dir.mkdir(exist_ok=True)
        
        self.agents: Dict[str, AgentConfig] = {}
        self.agent_actions: List[AgentAction] = []
        self.git_listings: Dict[str, GitAgentListing] = {}
        self.verified_agents: Set[str] = set()
        self.blocked_agents: Set[str] = set()
        self.agent_relationships: Dict[str, Set[str]] = {}  # agent_id -> related agents

    def _generate_agent_id(self, name: str, git_repo: str) -> str:
        """Generate unique agent ID."""
        agent_string = f"{name}_{git_repo}"
        return hashlib.sha256(agent_string.encode()).hexdigest()[:16]

    def register_agent_from_git(
        self,
        name: str,
        git_repo: str,
        git_branch: str = "main",
        config_path: str = "agent_config.json",
        agent_type: AgentType = AgentType.MONITORING,
        permissions: Optional[List[str]] = None
    ) -> Optional[AgentConfig]:
        """
        Register an agent from a git repository.
        
        Args:
            name: Agent name
            git_repo: Git repository URL
            git_branch: Git branch
            config_path: Path to config file in repo
            agent_type: Type of agent
            permissions: List of permissions
            
        Returns:
            AgentConfig if successful
        """
        agent_id = self._generate_agent_id(name, git_repo)
        
        # Clone repository
        repo_dir = self.workspace_dir / agent_id
        try:
            if repo_dir.exists():
                subprocess.run(["git", "fetch"], cwd=repo_dir, check=True, capture_output=True)
                subprocess.run(["git", "checkout", git_branch], cwd=repo_dir, check=True, capture_output=True)
                subprocess.run(["git", "pull"], cwd=repo_dir, check=True, capture_output=True)
            else:
                subprocess.run(["git", "clone", "-b", git_branch, git_repo, str(repo_dir)], check=True, capture_output=True)
            
            # Get commit hash
            result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo_dir, check=True, capture_output=True, text=True)
            commit_hash = result.stdout.strip()
            
            # Load config if exists
            config_file = repo_dir / config_path
            metadata = {}
            if config_file.exists():
                with open(config_file) as f:
                    metadata = json.load(f)
            
            # Create agent config
            agent_config = AgentConfig(
                agent_id=agent_id,
                name=name,
                agent_type=agent_type,
                git_repo=git_repo,
                git_branch=git_branch,
                config_path=config_path,
                status=AgentStatus.UNVERIFIED,
                created_at=datetime.utcnow().isoformat(),
                last_updated=datetime.utcnow().isoformat(),
                permissions=permissions or [],
                metadata=metadata
            )
            
            self.agents[agent_id] = agent_config
            self.agent_relationships[agent_id] = set()
            
            # Create git listing
            git_listing = GitAgentListing(
                repo_url=git_repo,
                branch=git_branch,
                commit_hash=commit_hash,
                agents=[agent_id],
                verified=False,
                last_sync=datetime.utcnow().isoformat()
            )
            self.git_listings[agent_id] = git_listing
            
            return agent_config
            
        except subprocess.CalledProcessError as e:
            print(f"Error cloning git repo: {e}")
            return None
        except Exception as e:
            print(f"Error registering agent: {e}")
            return None

    def verify_agent(self, agent_id: str, verification_method: str = "git_signature") -> bool:
        """
        Verify an agent using specified method.
        
        Args:
            agent_id: Agent identifier
            verification_method: Verification method
            
        Returns:
            True if verification successful
        """
        if agent_id not in self.agents:
            return False
        
        agent_config = self.agents[agent_id]
        repo_dir = self.workspace_dir / agent_id
        
        try:
            if verification_method == "git_signature":
                # Verify git signature (placeholder for actual GPG verification)
                result = subprocess.run(
                    ["git", "verify-commit", "HEAD"],
                    cwd=repo_dir,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    agent_config.status = AgentStatus.VERIFIED
                    self.verified_agents.add(agent_id)
                    self.git_listings[agent_id].verified = True
                    return True
            
            elif verification_method == "config_integrity":
                # Verify config file integrity
                config_file = repo_dir / agent_config.config_path
                if config_file.exists():
                    with open(config_file) as f:
                        config = json.load(f)
                    
                    # Check required fields
                    required_fields = ["name", "version", "author"]
                    if all(field in config for field in required_fields):
                        agent_config.status = AgentStatus.VERIFIED
                        self.verified_agents.add(agent_id)
                        return True
            
            return False
            
        except Exception as e:
            print(f"Error verifying agent {agent_id}: {e}")
            return False

    def link_agents(self, agent_id_1: str, agent_id_2: str) -> bool:
        """
        Link two agents for successive verification.
        
        Args:
            agent_id_1: First agent ID
            agent_id_2: Second agent ID
            
        Returns:
            True if linking successful
        """
        if agent_id_1 not in self.agents or agent_id_2 not in self.agents:
            return False
        
        # Check if both agents are verified
        if agent_id_1 not in self.verified_agents or agent_id_2 not in self.verified_agents:
            return False
        
        # Create bidirectional link
        self.agent_relationships[agent_id_1].add(agent_id_2)
        self.agent_relationships[agent_id_2].add(agent_id_1)
        
        return True

    def execute_agent_action(
        self,
        agent_id: str,
        action_type: str,
        target: str,
        parameters: Dict[str, Any]
    ) -> Optional[AgentAction]:
        """
        Execute an action through an agent.
        
        Args:
            agent_id: Agent identifier
            action_type: Type of action
            target: Action target
            parameters: Action parameters
            
        Returns:
            AgentAction if successful
        """
        if agent_id not in self.agents:
            return None
        
        # Check if agent is blocked
        if agent_id in self.blocked_agents:
            return None
        
        agent_config = self.agents[agent_id]
        
        # Check permissions
        if action_type not in agent_config.permissions:
            return None
        
        action_id = f"action_{uuid.uuid4().hex[:8]}"
        
        action = AgentAction(
            action_id=action_id,
            agent_id=agent_id,
            action_type=action_type,
            target=target,
            parameters=parameters,
            timestamp=datetime.utcnow().isoformat(),
            status="pending"
        )
        
        try:
            # Execute action (placeholder for actual execution logic)
            result = self._execute_action_logic(agent_config, action_type, target, parameters)
            
            action.status = "completed"
            action.result = result
            
            # Update agent last updated
            agent_config.last_updated = datetime.utcnow().isoformat()
            
        except Exception as e:
            action.status = "failed"
            action.result = {"error": str(e)}
        
        self.agent_actions.append(action)
        return action

    def _execute_action_logic(
        self,
        agent_config: AgentConfig,
        action_type: str,
        target: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute the actual action logic (placeholder)."""
        # This would contain the actual execution logic based on agent type
        return {
            "status": "success",
            "agent": agent_config.name,
            "action": action_type,
            "target": target,
            "timestamp": datetime.utcnow().isoformat()
        }

    def list_agents_from_git(self, repo_url: str, branch: str = "main") -> List[str]:
        """
        List available agents from a git repository.
        
        Args:
            repo_url: Git repository URL
            branch: Git branch
            
        Returns:
            List of agent IDs
        """
        # This would parse the git repository to find available agents
        # Placeholder implementation
        return []

    def sync_agent_git(self, agent_id: str) -> bool:
        """
        Sync an agent's git repository.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            True if successful
        """
        if agent_id not in self.agents:
            return False
        
        agent_config = self.agents[agent_id]
        repo_dir = self.workspace_dir / agent_id
        
        try:
            subprocess.run(["git", "fetch"], cwd=repo_dir, check=True, capture_output=True)
            subprocess.run(["git", "checkout", agent_config.git_branch], cwd=repo_dir, check=True, capture_output=True)
            subprocess.run(["git", "pull"], cwd=repo_dir, check=True, capture_output=True)
            
            # Update commit hash
            result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo_dir, check=True, capture_output=True, text=True)
            commit_hash = result.stdout.strip()
            
            self.git_listings[agent_id].commit_hash = commit_hash
            self.git_listings[agent_id].last_sync = datetime.utcnow().isoformat()
            agent_config.last_updated = datetime.utcnow().isoformat()
            
            return True
            
        except Exception as e:
            print(f"Error syncing agent {agent_id}: {e}")
            return False

    def block_agent(self, agent_id: str, reason: str = "") -> bool:
        """
        Block an agent from executing actions.
        
        Args:
            agent_id: Agent identifier
            reason: Reason for blocking
            
        Returns:
            True if successful
        """
        if agent_id not in self.agents:
            return False
        
        self.blocked_agents.add(agent_id)
        self.agents[agent_id].status = AgentStatus.BLOCKED
        
        if "blocked_reasons" not in self.agents[agent_id].metadata:
            self.agents[agent_id].metadata["blocked_reasons"] = []
        self.agents[agent_id].metadata["blocked_reasons"].append(reason)
        
        return True

    def unblock_agent(self, agent_id: str) -> bool:
        """
        Unblock an agent.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            True if successful
        """
        if agent_id in self.blocked_agents:
            self.blocked_agents.remove(agent_id)
            self.agents[agent_id].status = AgentStatus.VERIFIED if agent_id in self.verified_agents else AgentStatus.UNVERIFIED
            return True
        return False

    def get_linked_agents(self, agent_id: str) -> List[AgentConfig]:
        """Get all linked agents for an agent."""
        if agent_id not in self.agent_relationships:
            return []
        
        linked_configs = []
        for linked_id in self.agent_relationships[agent_id]:
            if linked_id in self.agents:
                linked_configs.append(self.agents[linked_id])
        
        return linked_configs

    def get_agent_actions(self, agent_id: str, limit: int = 50) -> List[AgentAction]:
        """Get action history for an agent."""
        agent_actions = []
        
        for action in reversed(self.agent_actions):
            if action.agent_id == agent_id:
                agent_actions.append(action)
                if len(agent_actions) >= limit:
                    break
        
        return agent_actions

    def get_statistics(self) -> Dict[str, Any]:
        """Get agent manager statistics."""
        status_distribution = {}
        for agent in self.agents.values():
            status = agent.status.name
            status_distribution[status] = status_distribution.get(status, 0) + 1
        
        return {
            "total_agents": len(self.agents),
            "verified_agents": len(self.verified_agents),
            "blocked_agents": len(self.blocked_agents),
            "total_actions": len(self.agent_actions),
            "status_distribution": status_distribution,
            "git_listings": len(self.git_listings),
            "linked_pairs": sum(len(rels) for rels in self.agent_relationships.values()) // 2
        }

    def export_state(self) -> str:
        """Export current state for recovery."""
        state = {
            "agents": {aid: asdict(agent) for aid, agent in self.agents.items()},
            "agent_actions": [asdict(action) for action in self.agent_actions],
            "git_listings": {aid: asdict(listing) for aid, listing in self.git_listings.items()},
            "verified_agents": list(self.verified_agents),
            "blocked_agents": list(self.blocked_agents),
            "agent_relationships": {aid: list(rels) for aid, rels in self.agent_relationships.items()},
            "export_timestamp": datetime.utcnow().isoformat()
        }
        return json.dumps(state, indent=2)

    def import_state(self, state_json: str) -> bool:
        """
        Import state for recovery.
        
        Args:
            state_json: JSON string of exported state
            
        Returns:
            True if import successful
        """
        try:
            state = json.loads(state_json)
            
            # Restore agents
            for aid, agent_dict in state.get("agents", {}).items():
                agent_dict["agent_type"] = AgentType(agent_dict["agent_type"])
                agent_dict["status"] = AgentStatus(agent_dict["status"])
                self.agents[aid] = AgentConfig(**agent_dict)
            
            # Restore actions
            for action_dict in state.get("agent_actions", []):
                self.agent_actions.append(AgentAction(**action_dict))
            
            # Restore git listings
            for aid, listing_dict in state.get("git_listings", {}).items():
                self.git_listings[aid] = GitAgentListing(**listing_dict)
            
            # Restore sets and relationships
            self.verified_agents = set(state.get("verified_agents", []))
            self.blocked_agents = set(state.get("blocked_agents", []))
            self.agent_relationships = {
                aid: set(rels) for aid, rels in state.get("agent_relationships", {}).items()
            }
            
            return True
        except Exception as e:
            print(f"Error importing state: {e}")
            return False

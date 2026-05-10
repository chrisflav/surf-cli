"""Pydantic v2 models for the SURF Research Cloud API schemas."""

from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, field_validator


class _Base(BaseModel):
    model_config = ConfigDict(extra="ignore")


class StatusEnum(str, Enum):
    available = "available"
    creating = "creating"
    deleted = "deleted"
    deleting = "deleting"
    failed = "failed"
    full = "full"
    in_use = "in-use"
    paused = "paused"
    pausing = "pausing"
    rebooting = "rebooting"
    resuming = "resuming"
    running = "running"
    unaccounted = "unaccounted"
    unhealthy = "unhealthy"
    unknown = "unknown"
    updating = "updating"


class ActionEnum(str, Enum):
    create = "create"
    delete = "delete"
    pause = "pause"
    purge = "purge"
    reboot = "reboot"
    release = "release"
    resume = "resume"
    update = "update"
    update_nsgs = "update_nsgs"
    update_storages = "update_storages"
    use = "use"


class WorkspaceActionStatusEnum(str, Enum):
    cancelled = "cancelled"
    failed = "failed"
    initialized = "initialized"
    pending = "pending"
    success = "success"


class ReasonEnum(str, Enum):
    ADMIN = "ADMIN"
    API = "API"
    ATTACHED_WORKSPACE_STATUS_CHANGE = "ATTACHED_WORKSPACE_STATUS_CHANGE"
    DEPLETED_WALLET = "DEPLETED_WALLET"
    LONG_PAUSED = "LONG_PAUSED"
    TRIGGER = "TRIGGER"
    UNACCOUNTED = "UNACCOUNTED"
    UNKNOWN = "UNKNOWN"
    WORKSPACE_EXPIRED = "WORKSPACE_EXPIRED"


class TagSchema(_Base):
    id: Optional[int] = None
    key: Optional[str] = None
    value: Optional[str] = None
    is_public: Optional[bool] = None


class MetaParameterSchema(_Base):
    key: Optional[str] = None
    value: Optional[str] = None


class MetaFlavourSchema(_Base):
    id: Optional[str] = None
    name: Optional[str] = None
    tags: list[TagSchema] = []
    status: Optional[str] = None
    category: Optional[str] = None
    subtitle: Optional[str] = None
    created_at: Optional[str] = None
    description: Optional[str] = None
    modified_at: Optional[str] = None
    support_url: Optional[str] = None
    accounting_products: list[int] = []


class MetaIpSchema(_Base):
    id: Optional[str] = None
    type: Optional[str] = None
    name: Optional[str] = None


class MetaNetworkSchema(_Base):
    id: Optional[str] = None
    type: Optional[str] = None
    name: Optional[str] = None


class MetaStorageSchema(_Base):
    id: Optional[str] = None
    type: Optional[str] = None
    name: Optional[str] = None
    index: Optional[int] = None
    volume_id: Optional[str] = None


class MetaAttachedToSchema(_Base):
    id: Optional[str] = None
    type: Optional[str] = None


class ActionResultResourceMetaItemSchema(_Base):
    type: Optional[str] = None
    value: Optional[str] = None
    sensitive: Optional[bool] = None


class WorkspaceAction(_Base):
    id: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None
    reason: Optional[str] = None
    action_parameters: Optional[Any] = None
    result: Optional[Any] = None
    time_created: Optional[str] = None
    time_updated: Optional[str] = None
    issuer_display_name: Optional[str] = None
    workspace: Optional[str] = None
    next_action: Optional[str] = None


class WorkspaceActionsRequest(_Base):
    action: ActionEnum
    parameters: Optional[dict[str, Any]] = None


class CreateMetaSchema(_Base):
    application_offering_id: str
    application_name: str
    application_icon: str
    application_type: str = "Compute"
    subscription_tag: str
    subscription_name: str
    subscription_group_id: str
    co_name: str
    host_name: str
    subscription_resource_type: str = "VM"
    flavours: list[MetaFlavourSchema] = []
    storages: list[MetaStorageSchema] = []
    ips: list[MetaIpSchema] = []
    networks: list[MetaNetworkSchema] = []
    dataset_names: list[str] = []
    dataset_ids: list[str] = []
    interactive_parameters: list[MetaParameterSchema] = []
    wallet_name: str
    wallet_id: str


class CreateApplicationSchema(_Base):
    co_id: str
    wallet_id: str
    description: str
    name: str
    meta: CreateMetaSchema
    additional_actions: list[WorkspaceActionsRequest] = []


class CreateComputeApplicationSchema(_Base):
    co_id: str
    wallet_id: str
    description: str
    name: str
    meta: CreateMetaSchema
    additional_actions: list[WorkspaceActionsRequest] = []
    end_time: str


class PatchedWorkspaceUpdate(_Base):
    name: Optional[str] = None
    end_time: Optional[str] = None


class PatchedWorkspaceChangeWalletRequest(_Base):
    wallet_id: Optional[str] = None
    wallet_name: Optional[str] = None


class ActionStorageSchema(_Base):
    id: str
    type: str = "Workspace"


class ActionRequestNsgsSchema(_Base):
    network_security_group_rules: list[str]


class ActionRequestStorageSchema(_Base):
    storages: list[ActionStorageSchema]


class BadRequestSchema(_Base):
    code: int = 400
    status: str = "Bad Request"
    message: list[str]


class LogsNotFoundSchema(_Base):
    code: int = 404
    status: str
    message: str


class ComputeResourceMetaSchema(_Base):
    id: Optional[str] = None
    ip: Optional[str] = None
    vm_id: Optional[str] = None
    image_id: Optional[str] = None
    cloud_type: Optional[str] = None
    public_key: Optional[str] = None
    flavor_name: Optional[str] = None
    secgroup_id: Optional[str] = None
    service_url: Optional[str] = None
    subscription: Optional[str] = None
    workspace_id: Optional[str] = None
    instance_user: Optional[str] = None
    resource_type: Optional[str] = None
    workspace_fqdn: Optional[str] = None
    application_type: Optional[str] = None
    boot_volume_size: Optional[int] = None
    boot_volume_type: Optional[str] = None
    min_os_disk_size: Optional[int] = None
    subscription_group: Optional[str] = None
    network_secgroup_id: Optional[str] = None
    terraform_script_version: Optional[float] = None


class ComputeActionResultResourceMetaSchema(_Base):
    id: Optional[Any] = None
    ip: Optional[Any] = None
    vm_id: Optional[Any] = None
    image_id: Optional[Any] = None
    cloud_type: Optional[Any] = None
    public_key: Optional[Any] = None
    flavor_name: Optional[Any] = None
    secgroup_id: Optional[Any] = None
    service_url: Optional[Any] = None
    subscription: Optional[Any] = None
    workspace_id: Optional[Any] = None
    instance_user: Optional[Any] = None
    resource_type: Optional[Any] = None
    workspace_fqdn: Optional[Any] = None
    application_type: Optional[Any] = None
    boot_volume_size: Optional[Any] = None
    boot_volume_type: Optional[Any] = None
    min_os_disk_size: Optional[Any] = None
    subscription_group: Optional[Any] = None
    network_secgroup_id: Optional[Any] = None
    terraform_script_version: Optional[Any] = None


class ComputeActionResultSchema(_Base):
    error: Optional[str] = None
    resource_meta: Optional[ComputeActionResultResourceMetaSchema] = None
    paused_at: Optional[str] = None
    security_groups: list[str] = []
    attached_storages: list[Any] = []
    detached_storages: list[Any] = []


class ComputeActionStorageSchema(_Base):
    id: Optional[str] = None
    index: Optional[int] = None
    status: Optional[str] = None
    volume_id: Optional[str] = None


class ComputeActionSchema(_Base):
    id: Optional[str] = None
    type: Optional[str] = None
    time_created: Optional[str] = None
    time_updated: Optional[str] = None
    status: Optional[str] = None
    workspace: Optional[str] = None
    result: Optional[ComputeActionResultSchema] = None


class ComputeMetaSchema(_Base):
    ips: list[MetaIpSchema] = []
    co_id: Optional[str] = None
    co_name: Optional[str] = None
    flavours: list[MetaFlavourSchema] = []
    networks: list[MetaNetworkSchema] = []
    owner_id: Optional[str] = None
    storages: list[MetaStorageSchema] = []
    co_scz_id: Optional[str] = None
    host_name: Optional[str] = None
    wallet_id: Optional[str] = None
    parameters: list[MetaParameterSchema] = []
    dataset_ids: list[str] = []
    wallet_name: Optional[str] = None
    owner_scz_id: Optional[str] = None
    workspace_id: Optional[str] = None
    dataset_names: list[str] = []
    workspace_fqdn: Optional[str] = None
    workspace_name: Optional[str] = None
    application_icon: Optional[str] = None
    application_name: Optional[str] = None
    application_type: Optional[str] = None
    subscription_tag: Optional[str] = None
    subscription_name: Optional[str] = None
    subscription_group_id: Optional[str] = None
    interactive_parameters: list[MetaParameterSchema] = []
    additional_user_actions: list[str] = []
    application_offering_id: Optional[str] = None
    subscription_resource_type: Optional[str] = None


class ComputeWorkspace(_Base):
    id: str
    resource_meta: Optional[ComputeResourceMetaSchema] = None
    active: Optional[bool] = None
    allowed_actions: list[str] = []
    deletable: Optional[bool] = None
    editable: Optional[bool] = None
    workspace_actions: Optional[list[ComputeActionSchema]] = None
    meta: Optional[ComputeMetaSchema] = None
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    end_time: Optional[str] = None
    time_created: Optional[str] = None
    time_deleted: Optional[str] = None
    wallet_id: Optional[str] = None
    owner_id: Optional[str] = None
    co_id: Optional[str] = None

    @field_validator("resource_meta", "meta", mode="before")
    @classmethod
    def _empty_to_none(cls, v: Any) -> Any:
        if not v:
            return None
        return v

    @field_validator("workspace_actions", mode="before")
    @classmethod
    def _empty_actions_to_none(cls, v: Any) -> Any:
        if v is not None and not isinstance(v, list):
            return None
        return v


class StorageResourceMetaSchema(_Base):
    id: Optional[str] = None
    volume_id: Optional[str] = None
    cloud_type: Optional[str] = None
    service_url: Optional[str] = None
    subscription: Optional[str] = None
    workspace_id: Optional[str] = None
    resource_type: Optional[str] = None
    workspace_fqdn: Optional[str] = None
    application_type: Optional[str] = None
    subscription_group: Optional[str] = None


class StorageActionResultResourceMetaSchema(_Base):
    id: Optional[Any] = None
    volume_id: Optional[Any] = None
    cloud_type: Optional[Any] = None
    service_url: Optional[Any] = None
    subscription: Optional[Any] = None
    workspace_id: Optional[Any] = None
    resource_type: Optional[Any] = None
    workspace_fqdn: Optional[Any] = None
    application_type: Optional[Any] = None
    subscription_group: Optional[Any] = None


class StorageActionResultSchema(_Base):
    error: Optional[str] = None
    resource_meta: Optional[StorageActionResultResourceMetaSchema] = None


class StorageActionSchema(_Base):
    id: Optional[str] = None
    type: Optional[str] = None
    time_created: Optional[str] = None
    time_updated: Optional[str] = None
    status: Optional[str] = None
    workspace: Optional[str] = None
    result: Optional[StorageActionResultSchema] = None


class StorageMetaSchema(_Base):
    ips: list[MetaIpSchema] = []
    co_id: Optional[str] = None
    co_name: Optional[str] = None
    flavours: list[MetaFlavourSchema] = []
    networks: list[MetaNetworkSchema] = []
    owner_id: Optional[str] = None
    co_scz_id: Optional[str] = None
    host_name: Optional[str] = None
    wallet_id: Optional[str] = None
    attached_to: list[MetaAttachedToSchema] = []
    storages: list[MetaStorageSchema] = []
    dataset_ids: list[str] = []
    wallet_name: Optional[str] = None
    owner_scz_id: Optional[str] = None
    workspace_id: Optional[str] = None
    dataset_names: list[str] = []
    workspace_name: Optional[str] = None
    application_icon: Optional[str] = None
    application_name: Optional[str] = None
    application_type: Optional[str] = None
    subscription_tag: Optional[str] = None
    subscription_name: Optional[str] = None
    subscription_group_id: Optional[str] = None
    interactive_parameters: Optional[MetaParameterSchema] = None
    additional_user_actions: list[str] = []
    application_offering_id: Optional[str] = None
    subscription_resource_type: Optional[str] = None


class StorageWorkspace(_Base):
    id: str
    resource_meta: Optional[StorageResourceMetaSchema] = None
    active: Optional[bool] = None
    allowed_actions: list[str] = []
    deletable: Optional[bool] = None
    editable: Optional[bool] = None
    workspace_actions: Optional[list[StorageActionSchema]] = None
    meta: Optional[StorageMetaSchema] = None
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    end_time: Optional[str] = None
    time_created: Optional[str] = None
    time_deleted: Optional[str] = None
    wallet_id: Optional[str] = None
    owner_id: Optional[str] = None
    co_id: Optional[str] = None

    @field_validator("resource_meta", "meta", mode="before")
    @classmethod
    def _empty_to_none(cls, v: Any) -> Any:
        if not v:
            return None
        return v

    @field_validator("workspace_actions", mode="before")
    @classmethod
    def _empty_actions_to_none(cls, v: Any) -> Any:
        if v is not None and not isinstance(v, list):
            return None
        return v


class IpResourceMetaSchema(_Base):
    id: Optional[str] = None
    ip_id: Optional[str] = None
    address: Optional[str] = None
    cloud_type: Optional[str] = None
    description: Optional[str] = None
    service_url: Optional[str] = None
    subscription: Optional[str] = None
    workspace_id: Optional[str] = None
    resource_type: Optional[str] = None
    workspace_fqdn: Optional[str] = None
    application_type: Optional[str] = None
    subscription_group: Optional[str] = None


class IpActionResultResourceMetaSchema(_Base):
    id: Optional[Any] = None
    ip_id: Optional[Any] = None
    address: Optional[Any] = None
    cloud_type: Optional[Any] = None
    description: Optional[Any] = None
    service_url: Optional[Any] = None
    subscription: Optional[Any] = None
    workspace_id: Optional[Any] = None
    resource_type: Optional[Any] = None
    workspace_fqdn: Optional[Any] = None
    application_type: Optional[Any] = None
    subscription_group: Optional[Any] = None


class IpActionResultSchema(_Base):
    error: Optional[str] = None
    resource_meta: Optional[IpActionResultResourceMetaSchema] = None


class IpActionSchema(_Base):
    id: Optional[str] = None
    type: Optional[str] = None
    time_created: Optional[str] = None
    time_updated: Optional[str] = None
    status: Optional[str] = None
    workspace: Optional[str] = None
    result: Optional[IpActionResultSchema] = None


class IpMetaSchema(_Base):
    ips: list[MetaIpSchema] = []
    co_id: Optional[str] = None
    co_name: Optional[str] = None
    flavours: list[MetaFlavourSchema] = []
    networks: list[MetaNetworkSchema] = []
    owner_id: Optional[str] = None
    storages: list[MetaStorageSchema] = []
    co_scz_id: Optional[str] = None
    host_name: Optional[str] = None
    wallet_id: Optional[str] = None
    attached_to: list[MetaAttachedToSchema] = []
    dataset_ids: list[str] = []
    wallet_name: Optional[str] = None
    owner_scz_id: Optional[str] = None
    workspace_id: Optional[str] = None
    dataset_names: list[str] = []
    workspace_name: Optional[str] = None
    application_icon: Optional[str] = None
    application_name: Optional[str] = None
    application_type: Optional[str] = None
    subscription_tag: Optional[str] = None
    subscription_name: Optional[str] = None
    subscription_group_id: Optional[str] = None
    interactive_parameters: list[MetaParameterSchema] = []
    additional_user_actions: list[str] = []
    application_offering_id: Optional[str] = None
    subscription_resource_type: Optional[str] = None


class IpWorkspace(_Base):
    id: str
    resource_meta: Optional[IpResourceMetaSchema] = None
    active: Optional[bool] = None
    allowed_actions: list[str] = []
    deletable: Optional[bool] = None
    editable: Optional[bool] = None
    workspace_actions: Optional[list[IpActionSchema]] = None
    meta: Optional[IpMetaSchema] = None
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    end_time: Optional[str] = None
    time_created: Optional[str] = None
    time_deleted: Optional[str] = None
    wallet_id: Optional[str] = None
    owner_id: Optional[str] = None
    co_id: Optional[str] = None

    @field_validator("resource_meta", "meta", mode="before")
    @classmethod
    def _empty_to_none(cls, v: Any) -> Any:
        if not v:
            return None
        return v

    @field_validator("workspace_actions", mode="before")
    @classmethod
    def _empty_actions_to_none(cls, v: Any) -> Any:
        if v is not None and not isinstance(v, list):
            return None
        return v


class NetworkResourceMetaSchema(_Base):
    id: Optional[str] = None
    vpc_id: Optional[str] = None
    router_id: Optional[str] = None
    subnet_id: Optional[str] = None
    cloud_type: Optional[str] = None
    network_id: Optional[str] = None
    description: Optional[str] = None
    service_url: Optional[str] = None
    subnet_cidr: Optional[str] = None
    network_name: Optional[str] = None
    subscription: Optional[str] = None
    workspace_id: Optional[str] = None
    resource_type: Optional[str] = None
    workspace_fqdn: Optional[str] = None
    application_type: Optional[str] = None
    subscription_group: Optional[str] = None


class NetworkActionResultResourceMetaSchema(_Base):
    id: Optional[Any] = None
    vpc_id: Optional[Any] = None
    router_id: Optional[Any] = None
    subnet_id: Optional[Any] = None
    cloud_type: Optional[Any] = None
    network_id: Optional[Any] = None
    description: Optional[Any] = None
    service_url: Optional[Any] = None
    subnet_cidr: Optional[Any] = None
    network_name: Optional[Any] = None
    subscription: Optional[Any] = None
    workspace_id: Optional[Any] = None
    resource_type: Optional[Any] = None
    workspace_fqdn: Optional[Any] = None
    application_type: Optional[Any] = None
    subscription_group: Optional[Any] = None


class NetworkActionResultSchema(_Base):
    error: Optional[str] = None
    resource_meta: Optional[NetworkActionResultResourceMetaSchema] = None


class NetworkActionSchema(_Base):
    id: Optional[str] = None
    type: Optional[str] = None
    time_created: Optional[str] = None
    time_updated: Optional[str] = None
    status: Optional[str] = None
    workspace: Optional[str] = None
    result: Optional[NetworkActionResultSchema] = None


class NetworkMetaSchema(_Base):
    ips: list[MetaIpSchema] = []
    co_id: Optional[str] = None
    co_name: Optional[str] = None
    flavours: list[MetaFlavourSchema] = []
    networks: list[MetaNetworkSchema] = []
    owner_id: Optional[str] = None
    storages: list[MetaStorageSchema] = []
    co_scz_id: Optional[str] = None
    host_name: Optional[str] = None
    wallet_id: Optional[str] = None
    attached_to: list[MetaAttachedToSchema] = []
    dataset_ids: list[str] = []
    wallet_name: Optional[str] = None
    owner_scz_id: Optional[str] = None
    workspace_id: Optional[str] = None
    dataset_names: list[str] = []
    workspace_name: Optional[str] = None
    application_icon: Optional[str] = None
    application_name: Optional[str] = None
    application_type: Optional[str] = None
    subscription_tag: Optional[str] = None
    subscription_name: Optional[str] = None
    subscription_group_id: Optional[str] = None
    interactive_parameters: list[MetaParameterSchema] = []
    additional_user_actions: list[str] = []
    application_offering_id: Optional[str] = None
    subscription_resource_type: Optional[str] = None


class NetworkWorkspace(_Base):
    id: str
    resource_meta: Optional[NetworkResourceMetaSchema] = None
    active: Optional[bool] = None
    allowed_actions: list[str] = []
    deletable: Optional[bool] = None
    editable: Optional[bool] = None
    workspace_actions: Optional[list[NetworkActionSchema]] = None
    meta: Optional[NetworkMetaSchema] = None
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    end_time: Optional[str] = None
    time_created: Optional[str] = None
    time_deleted: Optional[str] = None
    wallet_id: Optional[str] = None
    owner_id: Optional[str] = None
    co_id: Optional[str] = None

    @field_validator("resource_meta", "meta", mode="before")
    @classmethod
    def _empty_to_none(cls, v: Any) -> Any:
        if not v:
            return None
        return v

    @field_validator("workspace_actions", mode="before")
    @classmethod
    def _empty_actions_to_none(cls, v: Any) -> Any:
        if v is not None and not isinstance(v, list):
            return None
        return v


AnyWorkspace = ComputeWorkspace | StorageWorkspace | IpWorkspace | NetworkWorkspace


class PaginatedComputeWorkspaceList(_Base):
    count: int
    next: Optional[str] = None
    previous: Optional[str] = None
    results: list[ComputeWorkspace]


class PaginatedStorageWorkspaceList(_Base):
    count: int
    next: Optional[str] = None
    previous: Optional[str] = None
    results: list[StorageWorkspace]


class PaginatedIpWorkspaceList(_Base):
    count: int
    next: Optional[str] = None
    previous: Optional[str] = None
    results: list[IpWorkspace]


class PaginatedNetworkWorkspaceList(_Base):
    count: int
    next: Optional[str] = None
    previous: Optional[str] = None
    results: list[NetworkWorkspace]

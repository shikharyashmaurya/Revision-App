import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import textwrap
from io import BytesIO
import uuid

class RevisionApp:
    def __init__(self):
        self.initialize_session_state()
        self.handle_user_selection()
        self.create_ui()

    def initialize_session_state(self):
        if 'users' not in st.session_state:
            st.session_state.users = {}
        if 'current_user' not in st.session_state:
            st.session_state.current_user = None
        if 'user_sessions' not in st.session_state:
            st.session_state.user_sessions = {}

    def handle_user_selection(self):
        st.sidebar.title("User Selection")
        user_name = st.sidebar.text_input("Enter your name:")
        if st.sidebar.button("Set User"):
            if user_name:
                # Check if the username is already in use in this session
                if user_name in st.session_state.user_sessions:
                    st.sidebar.error(f"The name '{user_name}' is already in use. Please choose a different name.")
                else:
                    # Generate a unique session ID for this user
                    session_id = str(uuid.uuid4())
                    st.session_state.current_user = f"{user_name}_{session_id}"
                    st.session_state.user_sessions[user_name] = session_id
                    if st.session_state.current_user not in st.session_state.users:
                        st.session_state.users[st.session_state.current_user] = {}
                    st.success(f"User set to: {user_name}")
                    st.experimental_rerun()

    def create_ui(self):
        if st.session_state.current_user:
            display_name = st.session_state.current_user.split('_')[0]  # Extract the user's name without the session ID
            st.title(f"Concept Revision App - Welcome, {display_name}!")
            st.write('''Demo app don't have functionality like unlimited tree view expand, touch,expand,export map.
                No session history - after session your input information will be lost
                .For full functionality see - 
                  https://github.com/shikharyashmaurya/Revision-App''')
            
            # Navigation
            page = st.sidebar.selectbox("Choose a page", ["Tree View", "Mind Map", "Search"])

            if page == "Tree View":
                self.show_tree_view()
            elif page == "Mind Map":
                self.show_mind_map()
            elif page == "Search":
                self.show_search()
        else:
            st.title("Concept Revision App")
            st.write("Please enter your name in the sidebar to begin.")

    # The rest of the methods (show_tree_view, show_concept_details, show_mind_map, show_search, search_data, custom_tree_layout) 
    # remain the same as in the previous version, just ensure you're using st.session_state.current_user
    # to access the correct user data in st.session_state.users

    # Example of how to modify a method to use the new user identifier:
    def show_tree_view(self):
        st.header("Tree View")

        # Input for new concept
        new_key = st.text_input("Enter a new concept:")
        if st.button("Add Concept"):
            if new_key and new_key not in st.session_state.users[st.session_state.current_user]:
                st.session_state.users[st.session_state.current_user][new_key] = {'next': [], 'text': []}
                st.success(f"Added new concept: {new_key}")
                st.experimental_rerun()

        # Display concepts
        user_data = st.session_state.users[st.session_state.current_user]
        selected_concept = st.selectbox("Select a concept to view details:", 
                                        options=[""] + list(user_data.keys()))
        
        if selected_concept:
            self.show_concept_details(selected_concept)

    # ... (other methods remain the same, just ensure you're using st.session_state.current_user consistently)
    # def show_tree_view(self):
    #     st.header("Tree View")

    #     # Input for new concept
    #     new_key = st.text_input("Enter a new concept:")
    #     if st.button("Add Concept"):
    #         if new_key and new_key not in st.session_state.users[st.session_state.current_user]:
    #             st.session_state.users[st.session_state.current_user][new_key] = {'next': [], 'text': []}
    #             st.success(f"Added new concept: {new_key}")
    #             st.experimental_rerun()

    #     # Display concepts
    #     user_data = st.session_state.users[st.session_state.current_user]
    #     selected_concept = st.selectbox("Select a concept to view details:", 
    #                                     options=[""] + list(user_data.keys()))
        
    #     if selected_concept:
    #         self.show_concept_details(selected_concept)

    def show_concept_details(self, key):
        user_data = st.session_state.users[st.session_state.current_user]
        st.subheader(f"Concept: {key}")

        # Display related concepts
        st.write("Related Concepts:")
        for next_item in user_data[key]['next']:
            if st.button(f"Go to {next_item}", key=f"goto_{next_item}"):
                self.show_concept_details(next_item)
                return

        # Add related concept
        new_related = st.text_input(f"Add related concept to {key}:", key=f"related_{key}")
        if st.button(f"Add related to {key}", key=f"add_related_{key}"):
            if new_related and new_related not in user_data[key]['next']:
                if new_related not in user_data:
                    user_data[new_related] = {'next': [], 'text': []}
                user_data[key]['next'].append(new_related)
                st.success(f"Added {new_related} as related to {key}")
                st.experimental_rerun()

        # Display information
        st.write("Information:")
        for i, text_item in enumerate(user_data[key]['text']):
            st.text_area(f"Info {i+1}", value=text_item, key=f"info_{key}_{i}", height=100, disabled=True)

        # Add information
        new_info = st.text_area(f"Add information to {key}:", key=f"new_info_{key}")
        if st.button(f"Add info to {key}", key=f"add_info_{key}"):
            if new_info:
                user_data[key]['text'].append(new_info)
                st.success(f"Added new information to {key}")
                st.experimental_rerun()

    def show_mind_map(self):
        st.header("Mind Map")

        user_data = st.session_state.users[st.session_state.current_user]
        G = nx.Graph()
        for key, value in user_data.items():
            G.add_node(key)
            for next_item in value['next']:
                if next_item in user_data:
                    G.add_edge(key, next_item)

        pos = self.custom_tree_layout(G)

        plt.figure(figsize=(12, 8))
        nx.draw(G, pos, with_labels=False, node_color='lightblue', node_size=3000, alpha=0.8)

        for node, (x, y) in pos.items():
            lines = textwrap.wrap(node, width=10)
            plt.annotate('\n'.join(lines), (x, y), horizontalalignment='center', verticalalignment='center')

        plt.axis('off')

        buf = BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        
        st.image(buf, caption='Mind Map', use_column_width=True)

    def show_search(self):
        st.header("Search")

        query = st.text_input("Enter search term:")
        if st.button("Search"):
            results = self.search_data(query)
            if results:
                for key in results:
                    with st.expander(f"Concept: {key}"):
                        st.write("Related Concepts:")
                        for related in st.session_state.users[st.session_state.current_user][key]['next']:
                            st.write(f"- {related}")
                        st.write("Information:")
                        for info in st.session_state.users[st.session_state.current_user][key]['text']:
                            st.write(f"- {info}")
            else:
                st.write("No results found.")

    def search_data(self, query):
        query = query.lower()
        user_data = st.session_state.users[st.session_state.current_user]
        results = set()
        for key, value in user_data.items():
            if query in key.lower():
                results.add(key)
            for next_item in value['next']:
                if query in next_item.lower():
                    results.add(key)
            for text_item in value['text']:
                if query in text_item.lower():
                    results.add(key)
        return list(results)
    
    def custom_tree_layout(self, G):
        if not G.nodes():
            return {}

        def bfs_tree(root):
            tree = nx.bfs_tree(G, root)
            return tree

        def assign_positions(tree, root):
            pos = {}
            level_width = {}
            max_depth = 0

            def dfs(node, depth, order):
                nonlocal max_depth
                max_depth = max(max_depth, depth)
                if depth not in level_width:
                    level_width[depth] = 0
                level_width[depth] += 1
                children = list(tree.successors(node))
                if not children:
                    pos[node] = (order, -depth)
                    return order + 1
                
                start = order
                for child in children:
                    order = dfs(child, depth + 1, order)
                pos[node] = (start + (order - start - 1) / 2, -depth)
                return order

            dfs(root, 0, 0)

            # Normalize positions
            max_width = max(level_width.values()) if level_width else 1
            for node in pos:
                x, y = pos[node]
                pos[node] = (x / max_width, y / max_depth if max_depth != 0 else 0)

            return pos

        # Handle disconnected components
        components = list(nx.connected_components(G))
        if not components:
            return {}

        pos = {}
        y_offset = 0
        for component in components:
            subgraph = G.subgraph(component)
            root = max(subgraph.nodes(), key=lambda n: subgraph.degree(n))
            tree = bfs_tree(root)
            component_pos = assign_positions(tree, root)
            
            # Adjust y-positions for each component
            for node, (x, y) in component_pos.items():
                pos[node] = (x, y + y_offset)
            
            y_offset -= 1.5  # Increase vertical separation between components

        return pos

if __name__ == "__main__":
    app = RevisionApp()
